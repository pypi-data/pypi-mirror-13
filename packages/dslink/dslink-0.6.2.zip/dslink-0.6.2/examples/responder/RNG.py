import random

from dslink.DSLink import DSLink, Configuration
from dslink.Node import Node
from twisted.internet import reactor


class RNGDSLink(DSLink):
    def get_default_nodes(self, super_root):
        temp = Node("testnode", super_root)
        temp.set_type("number")
        temp.set_value(1)

        super_root.add_child(temp)

        return super_root

    def create_rng(self, data):
        name = data[1]["Name"]
        if self.responder.get_super_root().get("/%s" % name) is None:
            rng = Node(name, self.responder.get_super_root())
            rng.set_config("$is", "rng")
            rng.set_type("number")
            rng.set_value(0)
            self.responder.get_super_root().add_child(rng)
            delete = Node("delete", rng)
            delete.set_config("$is", "delete_rng")
            delete.set_invokable("config")
            rng.add_child(delete)
            self.rngs[name] = rng
            return [
                [
                    True
                ]
            ]
        return [
            [
                False
            ]
        ]

    def set_speed(self, data):
        self.speed = data[1]["Speed"]
        return [
            [
                True
            ]
        ]

    def delete_rng(self, data):
        del self.rngs[data[0].parent.name]
        self.responder.get_super_root().remove_child(data[0].parent.name)
        return [[]]

    def restore_rngs(self):
        for child in self.responder.get_super_root().children:
            node = self.responder.get_super_root().children[child]
            if node.get_config("$is") == "rng":
                self.rngs[node.name] = node

    def update_rng(self):
        for rng in self.rngs:
            if self.rngs[rng].is_subscribed():
                self.rngs[rng].set_value(random.randint(0, 1000))
        reactor.callLater(self.speed, self.update_rng)

if __name__ == "__main__":
    RNGDSLink(Configuration("python-rng", responder=True, requester=True))
