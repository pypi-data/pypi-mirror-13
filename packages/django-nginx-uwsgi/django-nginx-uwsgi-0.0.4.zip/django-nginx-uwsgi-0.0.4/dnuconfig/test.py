#~*~ coding: utf-8 ~*~
import settings
from dnuconfig import DNUConfig

YES = 'Yes'
NO = 'No'


if __name__ == '__main__':
    config = DNUConfig()
    config.set_domain('example.com')
    config.set_virtualenv(uses=True, directory='/srv/.env/my_virtualenv')

    config.set_django_settings_module(module=settings.DJANGO_SETTINGS_MODULE)

    config.set_module_to_run(settings.MODULE_TO_RUN)
    config.set_socks_dir(directory='/srv/socks')
    config.set_project_dir('/srv/www/myproject')
    config.set_app_name('myapp')

    #print(config.set_uwsgi_ini())
    print(config.set_nginx_conf())
