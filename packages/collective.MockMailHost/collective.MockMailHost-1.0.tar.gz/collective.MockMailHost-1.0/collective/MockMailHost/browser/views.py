from Products.Five.browser import BrowserView


class MyView(BrowserView):
    """ view for mockmailhost """
    def __call__(self):
        context = self.context
        if context.messages:
            return context.pop(0)
        return 'NO MESSAGE'
