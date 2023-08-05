class Base:
    def connect(self, configs):
        if configs['aws'][self.local_key]:
            self.connect_fake()
        else:
            self.connect_real(configs)
