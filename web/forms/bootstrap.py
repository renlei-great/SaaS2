class BootsTrap(object):
    """bootstrap基类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, filed in self.fields.items():
            filed.widget.attrs['class'] = 'form-control'
            filed.widget.attrs['placeholder'] = '请输入{}'.format(filed.label)