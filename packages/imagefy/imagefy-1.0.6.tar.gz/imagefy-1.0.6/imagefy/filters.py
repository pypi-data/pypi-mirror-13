VALID_WIDTH_AND_HEIGHT = (128, 2560)
VALID_BLUR_VALUE = (0, 100)
VALID_ROTATE_VALUE = (-360, 360)
VALID_ASPECT_RATIO_VALUE = (0, 100)
VALID_CROPM_X_AND_Y = (0, 10240)
VALID_CROP_POSITIONS = ['center', 'topright', 'bottomright', 'bottomleft', 'topleft']


class BaseFilter(object):
    def get_action(self):
        raise NotImplementedError('.get_action() must be implemented in subclass')


class BlackWhite(BaseFilter):
    def __init__(self):
        self.name = 'blackwhite'

    def get_action(self):
        return {
            'name': self.name
        }


class Sepia(BaseFilter):
    def __init__(self):
        self.name = 'sepia'

    def get_action(self):
        return {
            'name': self.name
        }


class Flip(BaseFilter):
    def __init__(self):
        self.name = 'flip'

    def get_action(self):
        return {
            'name': self.name
        }


class Mirror(BaseFilter):
    def __init__(self):
        self.name = 'mirror'

    def get_action(self):
        return {
            'name': self.name
        }


class Blur(BaseFilter):
    def __init__(self, value):
        min, max = VALID_BLUR_VALUE
        if value < min or value > max:
            raise ValueError('Invalid blur value (0-100 % accepted).')
        self.name = 'blur'
        self.value = value

    def get_action(self):
        return {
            'name': self.name,
            'params': {
                'value': self.value
            }
        }


class Rotate(BaseFilter):
    def __init__(self, value):
        min, max = VALID_ROTATE_VALUE
        if value < min or value > max:
            raise ValueError('Invalid rotation angle (-360 - 360 degrees accepted).')
        self.name = 'rotate'
        self.value = value

    def get_action(self):
        return {
            'name': self.name,
            'params': {
                'value': self.value
            }
        }


class Scale(BaseFilter):
    def __init__(self, width, height):
        min, max = VALID_WIDTH_AND_HEIGHT
        if width < min or width > max or height < min or height > max:
            raise ValueError('Invalid width or height (128 - 2560 px accepted).')
        self.name = 'scale'
        self.width = width
        self.height = height

    def get_action(self):
        return {
            'name': self.name,
            'params': {
                'width': self.width,
                'height': self.height
            }
        }


class Resize(BaseFilter):
    def __init__(self, width, height):
        min, max = VALID_WIDTH_AND_HEIGHT
        if width < min or width > max or height < min or height > max:
            raise ValueError('Invalid width or height (128 - 2560 px accepted).')
        self.name = 'resize'
        self.width = width
        self.height = height

    def get_action(self):
        return {
            'name': self.name,
            'params': {
                'width': self.width,
                'height': self.height
            }
        }


class Crop(BaseFilter):
    def __init__(self, width, height, position=None):
        min, max = VALID_WIDTH_AND_HEIGHT
        if width < min or width > max or height < min or height > max:
            raise ValueError('Invalid width or height (128 - 2560 px accepted).')
        if position and position not in VALID_CROP_POSITIONS:
            raise ValueError('Invalid position ("center", "topright", "bottomright", "bottomleft", "topleft" accepted).')
        self.name = 'crop'
        self.width = width
        self.height = height
        self.position = position or 'center'

    def get_action(self):
        return {
            'name': self.name,
            'params': {
                'width': self.width,
                'height': self.height,
                'type': self.position
            }
        }


class ManualCrop(BaseFilter):
    def __init__(self, width, height, x, y):
        min, max = VALID_WIDTH_AND_HEIGHT
        min_x_y, max_x_y = VALID_CROPM_X_AND_Y
        if width < min or width > max or height < min or height > max:
            raise ValueError('Invalid width or height (128 - 2560 px accepted).')
        if x < min_x_y or x > max_x_y or y < min_x_y or y > max_x_y:
            raise ValueError('Invalid starting point (0 - 10240 px accepted).')
        self.name = 'crop'
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def get_action(self):
        return {
            'name': self.name,
            'params': {
                'width': self.width,
                'height': self.height,
                'x': self.x,
                'y': self.y
            }
        }


class AspectRatio(BaseFilter):
    def __init__(self, width, height, position=None):
        min, max = VALID_ASPECT_RATIO_VALUE
        if width < min or width > max or height < min or height > max:
            raise ValueError('Invalid aspect ratio (0 - 100 accepted).')
        if position and position not in VALID_CROP_POSITIONS:
            raise ValueError('Invalid position ("center", "topright", "bottomright", "bottomleft", "topleft" accepted).')
        self.name = 'aspect'
        self.width = width
        self.height = height
        self.position = position or 'center'

    def get_action(self):
        return {
            'name': self.name,
            'params': {
                'width': self.width,
                'height': self.height,
                'type': self.position
            }
        }
