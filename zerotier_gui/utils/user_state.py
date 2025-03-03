class UserState:
    def __init__(self):
        self.my_id = None
        self.networks_cache = {}  # Кэш для сетей и их участников: {network_id: {'network': {...}, 'members': [...]}}

    def is_me(self, member_id):
        return self.my_id and member_id == self.my_id

    def clear_cache(self):
        self.networks_cache = {}

    def update_network_cache(self, network_id, network=None, members=None):
        if network_id not in self.networks_cache:
            self.networks_cache[network_id] = {'network': None, 'members': None}
        
        if network is not None:
            self.networks_cache[network_id]['network'] = network
        if members is not None:
            self.networks_cache[network_id]['members'] = members

    def get_cached_network(self, network_id):
        return self.networks_cache.get(network_id, {}).get('network')

    def get_cached_members(self, network_id):
        return self.networks_cache.get(network_id, {}).get('members')

    def update_networks_cache(self, networks):
        self.clear_cache()
        for network in networks:
            self.update_network_cache(network['id'], network=network)

# Создаем глобальный экземпляр для использования во всем приложении
state = UserState() 