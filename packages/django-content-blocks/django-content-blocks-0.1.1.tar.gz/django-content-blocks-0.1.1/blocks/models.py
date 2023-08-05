# coding=utf-8
from django.db import models
from trustedhtml.fields import TrustedHTMLField


class SiteBlock(models.Model):
    class Meta:
        verbose_name = u'текстовый блок'
        verbose_name_plural = u'текстовые блоки'

        unique_together = ['url', 'block_id', ]
        index_together = [['url', 'block_id', ]]

    url = models.CharField(verbose_name=u'URL', max_length=255, null=True, blank=True)
    block_id = models.CharField(verbose_name=u'идентификатор блока', max_length=25)
    text = TrustedHTMLField(verbose_name=u'текст')

    def __unicode__(self):
        if self.url:
            if len(self.url) > 25:
                url = self.url[:11] + '...' + self.url[-11:]
            else:
                url = self.url

            return u'{0} on {1}'.format(self.block_id, url)

        return self.block_id
