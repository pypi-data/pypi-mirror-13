from dashmat.core_modules.base import Module

class BootStrap(Module):

    @classmethod
    def css(kls):
        yield "bootstrap.css"
        yield "bootstrap-theme.min.css"

    @classmethod
    def npm_deps(kls):
        return {
              "react-bootstrap": "^0.28.1"
            }
