from django.forms import forms
from django.shortcuts import resolve_url
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class TagAutocompleteInput(forms.TextInput):
    class Media:
        css = {'all': ['javascript/library/select2-3.5.2/select2.css',
                       'javascript/library/select2-3.5.2/select2-bootstrap.css']}
        js = ['javascript/library/select2-3.5.2/select2.min.js',
              'javascript/library/select2-3.5.2/select2_locale_zh-CN.js']

    def __init__(self, allow_create_tag=True, suggestion_url=None, attrs=None):
        super(TagAutocompleteInput, self).__init__(attrs=attrs)
        self.allow_create_tag = allow_create_tag
        self.suggestion_url = suggestion_url

    def render(self, name, value, attrs=None):
        """
        :param name: 控件名字
        :param value: 默认值
        :param allow_create_tag: 是否创建新的Tag
        :param suggestion_url: 自动完成url
        :param attrs: 附加的html属性
        """
        create_new_tag = self.allow_create_tag or attrs and attrs.get('create_choice', True)
        suggestion_url = resolve_url(self.suggestion_url if self.suggestion_url else 'tag_suggestion')
        js = u"""<script>
        $(document).ready(function(){{
        $("#{id_for_label}").select2({{
        placeholder: '{placeholder}',
            tags:true,
            multiple: true,
             tokenSeparators: [",", " ",";"],
            ajax: {{
                url: "{url}",
                dataType: 'json',
                data: function (term) {{
                    return{{term: term}}
                }},
                results: function (data) {{
                    return {{results: data}};
                }}
            }},
            {create_choice}
            initSelection: function (element, callback) {{
                var data = [];
                $(element.val().split(",")).each(function (index,name) {{
                    data.push({{id: this, text: name}});
                }});
                callback(data);
            }},
            minimumInputLength: 1,
            triggerChange: true
        }})
        }})
        </script>
        """
        js = js.format(id_for_label=force_text(self.id_for_label('id_%s' % name)),
                       url=force_text(suggestion_url),
                       placeholder=attrs.get('placeholder', '') if attrs else '',
                       create_choice=""" createSearchChoice: function(term, data) {
                if ($(data).filter(function() {
                  return this.text.localeCompare(term) === 0;
                }).length === 0) {
                  return {
                    id: term,
                    text: term
                  };
                }
           },""" if create_new_tag else "")

        code = "%s %s" % (super(TagAutocompleteInput, self).render(name, value, attrs), js)
        return mark_safe(code)
