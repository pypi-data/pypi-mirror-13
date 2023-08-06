from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

import os
import timeside.core
from timeside.server.models import Selection, Item
from timeside.server.models import Processor, Preset, Experience, Task
from timeside.server.models import _PENDING, _DONE
from timeside.core.tools.test_samples import generateSamples


class Command(BaseCommand):
    help = "Setup and run a boilerplate for testing"
    cleanup =  True

    def processor_cleanup(self):
        for processor in Processor.objects.all():
            processor.delete()

    def result_cleanup(self):
        for result in Result.objects.all():
            result.delete()

    def handle(self, *args, **options):
       
        media_dir =  os.path.join('items','tests')
        samples_dir = os.path.join(settings.MEDIA_ROOT, media_dir)
 
        selection, c = Selection.objects.get_or_create(title='Tests')
        selection.items.count()
        if c | selection.items.count()==0:
            samples = generateSamples(samples_dir=samples_dir)

            for sample in samples.iteritems():
                filename, path = sample
                title = os.path.splitext(filename)[0]
                path = os.path.join(media_dir, filename)
                item, c = Item.objects.get_or_create(title=title, file=path)
                if not item in selection.items.all():
                    selection.items.add(item)
                if self.cleanup:
                    for result in item.results.all():
                        result.delete()

        presets = []
        blacklist =['decoder', 'live', 'gain', 'vamp']
        processors = timeside.core.processor.processors(timeside.core.api.IProcessor)
   
        for proc in processors:
            trig = True
            for black in blacklist:
                if black in proc.id():
                    trig = False
            if trig:
                processor, c = Processor.objects.get_or_create(pid=proc.id())
                preset, c = Preset.objects.get_or_create(processor=processor, parameters='{}')
                presets.append(preset)

        experience, c = Experience.objects.get_or_create(title='All')
        for preset in presets:
            if not preset in experience.presets.all():
                experience.presets.add(preset)

        task,c = Task.objects.get_or_create(experience=experience, selection=selection)
        if c | task.status != _DONE :
            task.status = _PENDING
            task.save()
        
 
