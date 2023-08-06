from django import forms


class AutoCompleteInput(forms.TextInput):
    """
    自动完成输入框
    https://github.com/meltingice/ajax-chosen
    """

    class Meta:
        css = {'all': ['zui/lib/chosen/chosen.min.css']}
        js = ['zui/lib/chosen/chosen.min.js',
              'javascript/library/ajax-chosen.min.js']

    def render(self, name, value, allow_create_tag=True, allow_multi_choices=False, suggestion_url=None, attrs=None):
        """
        渲染控件
        :param name: 控件名字
        :type name: str
        :param value: 初始值
        :type value: str
        :param allow_create_tag: 是否允许创建新的选项
        :type allow_create_tag: bool
        :param allow_multi_choices: 是否允许选择多个
        :type allow_multi_choices: bool
        :param suggestion_url: 键入推荐地址
        :type suggestion_url: str
        :param attrs: 附加选项
        :type attrs: dict
        :return:
        :rtype:
        """
        pass
