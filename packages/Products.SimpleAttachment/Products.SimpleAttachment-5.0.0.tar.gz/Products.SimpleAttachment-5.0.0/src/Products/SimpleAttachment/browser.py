from Products.Five import BrowserView
try:
    from plone.app.imagecropping.interfaces import IImageCroppingMarker
except ImportError:
    IImageCroppingMarker = None


class Helper(BrowserView):

    def is_cropping_supported(self, image=None):
        if IImageCroppingMarker is None:
            # plone.app.imagecropping is not available
            return False
        if image is None:
            # We can only give a general answer.
            return True
        # Give answer for this specific image.
        return IImageCroppingMarker.providedBy(image)
