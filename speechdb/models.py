from django.db import models

# Entity classes

class Author(models.Model):
    '''An ancient author'''
    
    name = models.CharField(max_length=64)
    wd = models.CharField('WikiData ID', max_length=32)
    urn = models.CharField(max_length=64)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Work(models.Model):
    '''An epic text'''

    class Language(models.TextChoices):
        GREEK = ('greek', 'Greek')
        LATIN = ('latin', 'Latin')
    
    title = models.CharField(max_length=64)
    wd = models.CharField('WikiData ID', max_length=32)
    urn = models.CharField(max_length=128)
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    lang = models.CharField(max_length=8, choices=Language.choices)
    
    class Meta:
        ordering = ['author', 'title']


    def __str__(self):
        return f'{self.author.name} {self.title}'

    
    def get_long_name(self):
        '''Return common name as a string'''
        return f'{self.author.name} {self.title}'


class Character(models.Model):
    '''An epic character'''
    
    class CharacterNumber(models.TextChoices):
        INDIVIDUAL = ('individual', 'Individual')
        COLLECTIVE = ('collective', 'Collective')
        OTHER = ('other', 'Other')


    class CharacterBeing(models.TextChoices):
        MORTAL = ('mortal', 'Mortal')
        DIVINE = ('divine', 'Divine')
        CREATURE = ('creature', 'Mythical Creature')
        OTHER = ('other', 'Other')
        

    class CharacterGender(models.TextChoices):
        NA = ('none', 'Unknown/not-applicable')
        NB = ('non-binary', 'Mixed/non-binary')
        FEMALE = ('female', 'Female')
        MALE = ('male', 'Male')

    
    name = models.CharField(max_length=64)
    being = models.CharField(max_length=16, choices=CharacterBeing.choices,
            default=CharacterBeing.MORTAL)
    number = models.CharField(max_length=16, choices=CharacterNumber.choices,
            default=CharacterNumber.INDIVIDUAL)
    gender = models.CharField(max_length=16, choices=CharacterGender.choices,
            default=CharacterGender.NA)
    wd = models.CharField('WikiData ID', max_length=32, null=True)
    manto = models.CharField('MANTO ID', max_length=32, null=True)


    class Meta:
        ordering = ['name']


    def __str__(self):
        return self.name


class CharacterInstance(models.Model):
    '''A character engaged in a speech'''
    
    name = models.CharField(max_length=64)
    being = models.CharField(max_length=16, 
            choices=Character.CharacterBeing.choices,
            default=Character.CharacterBeing.MORTAL)
    number = models.CharField(max_length=16,
            choices=Character.CharacterNumber.choices,
            default=Character.CharacterNumber.INDIVIDUAL)
    gender = models.CharField(max_length=16,
            choices=Character.CharacterGender.choices,
            default=Character.CharacterGender.NA)
    char = models.ForeignKey(Character, related_name='instances', 
            null=True, on_delete=models.PROTECT)
    disg = models.ForeignKey(Character, related_name='disguises', 
            null=True, on_delete=models.PROTECT)
    anon = models.BooleanField(default=False)
    #TODO tuple (char, context) should be unique
    context = models.CharField(max_length=128)
    tags = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.get_long_name()
    
    def get_long_name(self):
        '''returns char name, including instance name and/or disguise'''
        name = self.name
        
        if self.char is not None:
            if name != self.char.name:
                name += '/' + self.char.name
        
        return name


class SpeechCluster(models.Model):
    '''A group of related speeches'''
    
    class Meta:
        ordering = ['speech']
        
    def get_spkr_str(self):
        '''Return speaker list as a string'''
        chars = []
        for speech in self.speech_set.all():
            chars.extend([str(c) for c in speech.spkr.all()])
        chars = sorted(set(chars))
        return ', '.join(chars)
    
    def get_addr_str(self):
        '''Return addressee list as a string'''
        chars = []
        for speech in self.speech_set.all():
            chars.extend([str(c) for c in speech.addr.all()])
        chars = sorted(set(chars))
        return ', '.join(chars)
        
    def get_chars_str(self):
        chars = []
        for speech in self.speech_set.all():
            chars.extend([str(c) for c in speech.spkr.all()])
            chars.extend([str(c) for c in speech.addr.all()])
        chars = sorted(set(chars))
        return ', '.join(chars)
        

class Speech(models.Model):
    '''A direct speech instance'''
    
    class SpeechType(models.TextChoices):
        SOLILOQUY = ('S', 'Soliloquy')
        MONOLOGUE = ('M', 'Monologue')
        DIALOGUE = ('D', 'Dialogue')
        GENERAL = ('G', 'General')
    
    cluster = models.ForeignKey(SpeechCluster, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    type = models.CharField(max_length=1, choices=SpeechType.choices)
    seq = models.IntegerField()
    l_fi = models.CharField('first line', max_length=8)
    l_la = models.CharField('last line', max_length=8)
    spkr = models.ManyToManyField(CharacterInstance, related_name='speeches')
    addr = models.ManyToManyField(CharacterInstance, related_name='addresses',
             blank=True)
    # TODO should be unique per cluster
    part = models.IntegerField()
    
    class Meta:
        ordering = ['work', 'seq']
    
    def __str__(self):
        return f'{self.work} {self.l_fi}-{self.l_la}'
        
    def get_urn(self):
        '''Return CTS URN for the whole speech'''
        return f'{self.work.urn}:{self.l_fi}-{self.l_la}'
        
    def get_spkr_str(self):
        '''Return speaker list as a string'''
        return ', '.join([str(s) for s in self.spkr.all()])
    
    def get_addr_str(self):
        '''Return speaker list as a string'''
        return ', '.join([str(s) for s in self.addr.all()])
        
    def get_short_type(self):
        '''Return one-char type designation'''
        t = self.type
        if t == 'D' or t == 'G':
            t += str(self.part)
        return t