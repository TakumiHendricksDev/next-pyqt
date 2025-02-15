from abc import ABC, abstractmethod

class NextPyComponentLifecycle(ABC):
    @abstractmethod
    def component_did_mount(self):
        pass

    @abstractmethod
    def component_did_unmount(self):
        pass