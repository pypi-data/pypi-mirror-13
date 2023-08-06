'''
Created on 16/12/2015

@author: luisza
'''


from django.forms.widgets import Select
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from crdist.models import Province, Canton, District
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from crdist.utils import obj_2_hexa


class DistrictSelect(Select):

    def render(self, name, value, attrs=None, choices=()):
        prov_value = []
        dist = None
        canton = None
        prov = None
        if value is None or value==-1 or value=="-1":
            value = ''
        else:
            dist = District.objects.get(pk=value)
            canton = dist.canton.pk
            prov_value.append(str(dist.canton.province.pk))
            prov = dist.canton.province.pk

        prov_attrs = self.build_attrs(attrs, name='province_' + name)
        prov_attrs['id'] = 'id_province_' + name
        prov_attrs['onchange'] = 'load_canton(this, undefined)'
        output = ['<label for="%s">%s: </label>' % (prov_attrs['id'], _('Province')) ,
                  format_html('<select{}>', flatatt(prov_attrs))]
        output.append(self.render_province(prov_value))
        output.append('</select>')

        cant_att = {'id': 'div_canton_' + name, 'href': reverse('crdist_canton') + '?name=' + name}
        dist_att = {'id': 'div_district_' + name, 'href': reverse('crdist_district') + '?name=' + name }

        if attrs:
            nattrs = self.build_attrs(attrs)
            del nattrs['id']
            if nattrs:
                nattrs = obj_2_hexa(nattrs)
                dist_att['href'] = dist_att['href'] + "&attrs=" + nattrs
                cant_att['href'] = cant_att['href'] + "&attrs=" + nattrs

        output.append(format_html('<div{}></div>', flatatt(cant_att)))
        output.append(format_html('<div{}></div>', flatatt(dist_att)))
        if not dist is None:
            output.append("""<input type="hidden" name="err_canton_%s" class="crdist_onerror" value="%d"
            initial="%d" />""" % (name, prov, canton))
            output.append("""<input type="hidden" name="err_district_%s" class="crdist_onerror" value="%d" 
            initial="%d" />""" % (name, canton, dist.pk))
        return mark_safe('\n'.join(output))

    def render_province(self, selected_value=[]):
        options = [self.render_option(selected_value, -1, '  ---  ')]
        for prov in Province.objects.all():
            options.append(self.render_option(selected_value, prov.pk, prov.name))
        return '\n'.join(options)
    
    class Media:
        js = ('crdist/form.%sjs' % ("min." if not settings.DEBUG else ""),)

