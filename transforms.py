def transform(self, x, y):
    return self.transform_perspective(x, y)
    #return self.transform_2D(x, y)


def transform_2D(self, x, y):
    return (x, y)


def transform_perspective(self, x, y):
    lin_y = (y / self.height) * self.perspective_point_y

    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y

    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y

    factor_y = diff_y / self.perspective_point_y
    factor_y = pow(factor_y, 2)
    """
        1 when diff_y == self.height (at the low point)
        .
        .
        0 when diff_y = 0 (self.perspective_point_y == tr_y)
    """

    tr_x = self.perspective_point_x + diff_x * factor_y
    tr_y = (1 - factor_y) * self.perspective_point_y

    return int(tr_x), int(tr_y)

