class UserState:
    def __init__(self):
        self.my_id = None  # ZeroTier node ID (from zerotier-cli info)
        self.user_id = None  # ZeroTier API user ID (UUID)
        self.user_data = None  # Complete user data from API
        self.networks_cache = (
            {}
        )  # Cache for networks and their members: {network_id: {'network': {...}, 'members': [...]}}

    def is_me(self, member_id):
        """Check if the given member ID matches the current user's ID."""
        return self.my_id and member_id == self.my_id

    def clear_cache(self):
        """Clear the networks cache."""
        self.networks_cache = {}

    def update_network_cache(self, network_id, network=None, members=None):
        """Update the cache for a specific network.
        
        Args:
            network_id: The ID of the network to update
            network: The network data to cache (optional)
            members: The network members to cache (optional)
        """
        if network_id not in self.networks_cache:
            self.networks_cache[network_id] = {"network": None, "members": None}

        if network is not None:
            self.networks_cache[network_id]["network"] = network
        if members is not None:
            self.networks_cache[network_id]["members"] = members

        # If both parameters are None, remove the entry from the cache completely
        if network is None and members is None:
            if network_id in self.networks_cache:
                del self.networks_cache[network_id]

    def get_cached_network(self, network_id):
        """Get cached network data for the specified network ID."""
        return self.networks_cache.get(network_id, {}).get("network")

    def get_cached_members(self, network_id):
        """Get cached members for the specified network ID."""
        return self.networks_cache.get(network_id, {}).get("members")

    def update_networks_cache(self, networks):
        """Update the cache with a list of networks."""
        self.clear_cache()
        for network in networks:
            self.update_network_cache(network["id"], network=network)


# Create a global instance for use throughout the application
state = UserState()
