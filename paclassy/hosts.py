from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'teacher', 'apps.teacher.urls', name='teacher'),
    host(r'student', 'apps.student.urls', name='student'),
    host(r'admin', 'apps.adminpanel.urls', name='adminpanel'),
    host(r'www', 'paclassy.urls', name='www'),
    host(r'', 'paclassy.urls', name='root'),
)
