import copy

class ApiObject(object):
  def __init__(self, body):
    self._body = body

  def __repr__(self):
    return repr(self._body)

  def to_json(self):
    return copy.deepcopy(self._body)


class Assignments(ApiObject):
  def get(self, key):
    return self._body.get(key)

  def __getitem__(self, key):
    return self._body[key]

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self._body == other._body
    else:
      return False

class Bounds(ApiObject):
  @property
  def max(self):
    return self._body.get('max')

  @property
  def min(self):
    return self._body.get('min')


class CategoricalValue(ApiObject):
  @property
  def name(self):
    return self._body.get('name')


class Client(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def created(self):
    return self._body.get('created')

  @property
  def name(self):
    return self._body.get('name')


class Experiment(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def created(self):
    return self._body.get('created')

  @property
  def name(self):
    return self._body.get('name')

  @property
  def type(self):
    return self._body.get('type')

  @property
  def state(self):
    return self._body.get('state')

  @property
  def parameters(self):
    _parameters = self._body.get('parameters', [])
    return [Parameter(p) for p in _parameters]

  @property
  def metric(self):
    _metric = self._body.get('metric')
    return Metric(_metric) if _metric is not None else None

  @property
  def progress(self):
    _progress = self._body.get('progress')
    return Progress(_progress) if _progress is not None else None

  @property
  def client(self):
    return self._body.get('client')


class Metric(ApiObject):
  @property
  def name(self):
    return self._body.get('name')


class Observation(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def created(self):
      return self._body.get('created')

  @property
  def assignments(self):
    _assignments = self._body.get('assignments')
    return Assignments(_assignments) if _assignments is not None else None

  @property
  def value(self):
    return self._body.get('value')

  @property
  def value_stddev(self):
    return self._body.get('value_stddev')

  @property
  def failed(self):
    return self._body.get('failed')

  @property
  def suggestion(self):
    return self._body.get('suggestion')

  @property
  def experiment(self):
    return self._body.get('experiment')

  @property
  def timestamp(self):
      return self._body.get('timestamp')


class Paging(ApiObject):
  @property
  def before(self):
    return self._body.get('before')

  @property
  def after(self):
    return self._body.get('after')


class Pagination(ApiObject):
  def __init__(self, data_cls, body):
    super(Pagination, self).__init__(body)
    self.data_cls = data_cls

  @property
  def count(self):
    return self._body.get('count')

  @property
  def data(self):
    _data = self._body.get('data')
    return [self.data_cls(d) for d in _data]

  @property
  def paging(self):
    _paging = self._body.get('paging')
    return Paging(_paging) if _paging is not None else None


class Parameter(ApiObject):
  @property
  def name(self):
    return self._body.get('name')

  @property
  def type(self):
    return self._body.get('type')

  @property
  def bounds(self):
    _bounds = self._body.get('bounds')
    return Bounds(_bounds) if _bounds is not None else None

  @property
  def categorical_values(self):
    _categorical_values = self._body.get('categorical_values', [])
    return [CategoricalValue(cv) for cv in _categorical_values]

  @property
  def transformation(self):
    return self._body.get('transformation')


class Progress(ApiObject):
  @property
  def observation_count(self):
    return self._body.get('observation_count')

  @property
  def best_observation(self):
    _observation = self._body.get('best_observation')
    return Observation(_observation) if _observation is not None else None

  @property
  def last_observation(self):
    _observation = self._body.get('last_observation')
    return Observation(_observation) if _observation is not None else None

  @property
  def first_observation(self):
    _observation = self._body.get('first_observation')
    return Observation(_observation) if _observation is not None else None


class Role(ApiObject):
  @property
  def role(self):
    return self._body.get('role')

  @property
  def client(self):
    _client = self._body.get('client')
    return Client(_client) if _client is not None else None

  @property
  def user(self):
    _user = self._body.get('user')
    return User(_user) if _user is not None else None


class Suggestion(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def created(self):
    return self._body.get('created')

  @property
  def state(self):
    return self._body.get('state')

  @property
  def assignments(self):
    _assignments = self._body.get('assignments')
    return Assignments(_assignments) if _assignments is not None else None

  @property
  def experiment(self):
    return self._body.get('experiment')


class User(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def name(self):
    return self._body.get('name')

  @property
  def email(self):
    return self._body.get('email')


class Worker(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def suggestion(self):
    _suggestion = self._body.get('suggestion')
    return Suggestion(_suggestion) if _suggestion else None

  @property
  def claimed_time(self):
    return self._body.get('claimed_time')
