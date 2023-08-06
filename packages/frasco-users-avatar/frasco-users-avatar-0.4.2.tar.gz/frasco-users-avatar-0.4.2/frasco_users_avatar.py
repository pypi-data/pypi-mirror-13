from frasco import Feature, action, current_app, request, url_for
import hashlib
import urllib
import math
import random
import base64
import requests

try:
    from frasco_upload import url_for_upload
except ImportError:
    pass


def svg_to_base64_data(svg):
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg)


class UsersAvatarFeature(Feature):
    name = "users_avatar"
    requires = ["users"]
    defaults = {"avatar_column": "avatar_filename",
                "url": None,
                "avatar_size": 80,
                "url_scheme": "",
                "add_flavatar_route": False,
                "add_avatar_route": True,
                "try_gravatar": True,
                "force_gravatar": False,
                "gravatar_size": None,
                "gravatar_email_column": None,
                "gravatar_default": "mm",
                "force_flavatar": False,
                "flavatar_size": "100%",
                "flavatar_name_column": None,
                "flavatar_font_size": 80,
                "flavatar_text_dy": "0.32em",
                "flavatar_length": 1,
                "flavatar_text_color": "#ffffff",
                "flavatar_bg_colors": ["#5A8770", "#B2B7BB", "#6FA9AB", "#F5AF29", "#0088B9", "#F18636", "#D93A37", "#A6B12E", "#5C9BBC", "#F5888D", "#9A89B5", "#407887", "#9A89B5", "#5A8770", "#D33F33", "#A2B01F", "#F0B126", "#0087BF", "#F18636", "#0087BF", "#B2B7BB", "#72ACAE", "#9C8AB4", "#5A8770", "#EEB424", "#407887"]}

    def init_app(self, app):
        user_model = app.features.models.ensure_model(app.features.users.model,
            **dict([(self.options["avatar_column"], str)]))
        if not hasattr(user_model, 'avatar_url'):
            user_model.avatar_url = property(self.get_avatar_url)

        def flavatar(name, bgcolorstr=None):
            if bgcolorstr is None:
                bgcolorstr = request.args.get('bgcolorstr')
            return self.generate_first_letter_avatar_svg(
                name, bgcolorstr, request.args.get('size')), 200, {'Content-Type': 'image/svg+xml'}

        if self.options['add_avatar_route']:
            @app.route('/avatar/<hash>/<name>')
            def avatar(hash, name):
                if self.options['try_gravatar']:
                    size = self.options['gravatar_size'] or self.options["avatar_size"]
                    try:
                        r = requests.get(self._format_gravatar_url(hash, s=size, d=404, _scheme='http'))
                        if r.status_code != 404:
                            return r.content, 200, {'Content-Type': r.headers['content-type']}
                    except Exception:
                        pass
                return flavatar(name, hash)

        if self.options['add_flavatar_route']:
            app.add_url_rule('/flavatar/<name>.svg', 'flavatar', flavatar)
            app.add_url_rule('/flavatar/<name>/<bgcolorstr>.svg', 'flavatar', flavatar)

    def get_avatar_url(self, user):
        filename = getattr(user, self.options["avatar_column"], None)
        if filename:
            return url_for_upload(filename)
        email = getattr(user, self.options["gravatar_email_column"] or
            current_app.features.users.options["email_column"], None)
        hash = hashlib.md5(email.lower()).hexdigest()
        username = getattr(user, self.options["flavatar_name_column"] or
            current_app.features.users.options["username_column"], None)
        if self.options["force_flavatar"] and (email or username):
            if self.options['add_flavatar_route']:
                return url_for('flavatar', name=username, bgcolorstr=hash, _external=True,
                    _scheme=self.options['url_scheme'])
            return svg_to_base64_data(self.generate_first_letter_avatar_svg(username or email, username))
        if self.options["force_gravatar"] and email:
            return self.get_gravatar_url(email)
        if self.options['url']:
            return self.options["url"].format(email=email, email_hash=hash, username=username)
        if self.options['add_avatar_route']:
            return url_for('avatar', hash=hash, name=username, _external=True,
                    _scheme=self.options['url_scheme'])

    @action("gravatar_url", default_option="email", as_="gravatar_url")
    def get_gravatar_url(self, email, size=None, default=None):
        hash = hashlib.md5(email.lower()).hexdigest()
        size = size or self.options['gravatar_size'] or self.options["avatar_size"]
        default = default or self.options['gravatar_default']
        return self._format_gravatar_url(hash, s=size, d=default)

    def _format_gravatar_url(self, hash, _scheme=None, **kwargs):
        return ("%s://www.gravatar.com/avatar/%s?%s" % (self.options["url_scheme"] or _scheme, hash,
            urllib.urlencode({k: v for k, v in kwargs.items() if v is not None}))).lstrip(':')

    def generate_first_letter_avatar_svg(self, name, bgcolorstr=None, size=None):
        size = size or self.options['flavatar_size'] or self.options["avatar_size"]
        if size and isinstance(size, int):
            size = "%spx" % size

        svg_tpl = ('<svg xmlns="http://www.w3.org/2000/svg" pointer-events="none" viewBox="0 0 100 100" '
               'width="%(w)s" height="%(h)s" style="background-color: %(bgcolor)s;">%(letter)s</svg>')

        char_svg_tpl = ('<text text-anchor="middle" y="50%%" x="50%%" dy="%(dy)s" '
                        'pointer-events="auto" fill="%(fgcolor)s" font-family="'
                        'HelveticaNeue-Light,Helvetica Neue Light,Helvetica Neue,Helvetica, Arial,Lucida Grande, sans-serif" '
                        'style="font-weight: 400; font-size: %(size)spx">%(char)s</text>')

        if not name:
            text = '?'
        else:
            text = name[0:min(self.options['flavatar_length'], len(name))]
        colors_len = len(self.options['flavatar_bg_colors'])
        if bgcolorstr:
            bgcolor = sum([ord(c) for c in bgcolorstr]) % colors_len
        elif ord(text[0]) < 65:
            bgcolor = random.randint(0, colors_len - 1)
        else:
            bgcolor = int(math.floor((ord(text[0]) - 65) % colors_len))

        return svg_tpl % {
            'bgcolor': self.options['flavatar_bg_colors'][bgcolor],
            'w': size,
            'h': size,
            'letter': char_svg_tpl % {
                'dy': self.options['flavatar_text_dy'],
                'fgcolor': self.options['flavatar_text_color'],
                'size': self.options['flavatar_font_size'],
                'char': text
            }
        }