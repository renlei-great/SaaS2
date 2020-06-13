class BootsTrap(object):
    """bootstrap基类"""
    bootstrap_class_exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, filed in self.fields.items():
            if name in self.bootstrap_class_exclude:
                continue
            cla = filed.widget.attrs.get('class', '')
            filed.widget.attrs['class'] = f'{cla} form-control'
            filed.widget.attrs['placeholder'] = '请输入{}'.format(filed.label)