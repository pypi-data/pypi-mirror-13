import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class RelatedDatasetsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'related_datasets')

    def before_map(self, map):
        return map

    def after_map(self, map):
        map.connect('fetch_related', '/exv/fetch/related', controller='ckanext.related_datasets.controllers.related_datasets_controller:RelatedDatasetsController',
                    action='list')
    	return map