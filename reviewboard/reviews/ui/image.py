from django.utils.html import escape
from djblets.util.templatetags.djblets_images import crop_image

from reviewboard.reviews.ui.base import FileAttachmentReviewUI


class ImageReviewUI(FileAttachmentReviewUI):
    name = 'Image'
    supported_mimetypes = ['image/*']

    js_model_class = 'RB.ImageReviewable'
    js_view_class = 'RB.ImageReviewableView'

    def get_js_model_data(self):
        return {
            'imageURL': self.obj.file.url,
            'fileAttachmentID': self.obj.id,
        }

    def serialize_comments(self, comments):
        result = {}
        serialized_comments = \
            super(ImageReviewUI, self).serialize_comments(comments)

        for serialized_comment in serialized_comments:
            try:
                position = '%(x)sx%(y)s+%(width)s+%(height)s' \
                           % serialized_comment
            except KeyError:
                # It's possible this comment was made before the review UI
                # was provided, meaning it has no data. If this is the case,
                # ignore this particular comment, since it doesn't have a
                # region.
                continue

            result.setdefault(position, []).append(serialized_comment)

        return result

    def get_comment_thumbnail(self, comment):
        try:
            x = int(comment.extra_data['x'])
            y = int(comment.extra_data['y'])
            width = int(comment.extra_data['width'])
            height = int(comment.extra_data['height'])
        except (KeyError, ValueError):
            # This may be a comment from before we had review UIs. Or,
            # corrupted data. Either way, don't display anything.
            return None

        image_url = crop_image(comment.file_attachment.file,
                               x, y, width, height)

        return u'<img src="%s" width="%s" height="%s" alt="%s" />' % \
               (image_url, width, height, escape(comment.text))
