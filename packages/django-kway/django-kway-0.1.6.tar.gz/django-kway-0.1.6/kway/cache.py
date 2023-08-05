# -*- coding: utf-8 -*-

from django.core.cache import get_cache

from kway import settings, utils
    

def get_value_for_key(key, default_value = None):
    
    cache = get_cache(settings.KWAY_CACHE_NAME)
    localized_key = utils.get_localized_key(key)
    
    value = None
    
    if cache:
        
        value = cache.get(localized_key, None)
        
        if value:
            
            cache.set(localized_key, value)
        
        cache.close()
            
    return value or default_value
    
    
def set_value_for_key(key, value):
    
    cache = get_cache(settings.KWAY_CACHE_NAME)
    localized_key = utils.get_localized_key(key)
    
    if cache:
        
        if value:
            cache.set(localized_key, value)
        else:
            cache.delete(localized_key)
        
        cache.close()
        
    return value
    
    
def update_values_post_save(sender, instance, **kwargs):
    
    if kwargs['created']:
        return
        
    cache = get_cache(settings.KWAY_CACHE_NAME)
    
    if cache:
        
        for language in settings.KWAY_LANGUAGES:
            
            language_code = language[0]
            localized_key = utils.get_localized_key(instance.key, language_code)
            localized_value_field_name = utils.get_localized_value_field_name(language_code)
            localized_value = getattr(instance, localized_value_field_name)
            
            cache.set(localized_key, localized_value)
            
        cache.close()
        
        