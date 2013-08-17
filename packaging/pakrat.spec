%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%define pakrat_dir %(tar -tzf %{SOURCE0} | egrep '^(\./)?pakrat(-[^/]*)?/$')

name: pakrat
summary: A Python library for mirroring and versioning YUM repositories
version: 0.3.0
release: 1%{?dist}
buildarch: noarch
license: MIT
source0: %{name}.tar.gz
buildrequires: yum, createrepo, python-setuptools-devel
requires: yum, createrepo

%description
Pakrat is a Pythonic library used to mirror YUM repositories using
a snapshot-based approach with common package file storage to reduce
the footprint of storing versioned repositories. Pakrat uses the
standard YUM repository configuration format and supports baseurls
as well as mirrorlists. Pakrat provides both a command-line
interface as well as an easy-to-use Python api for integration with
other projects.

%prep
%setup -n %{pakrat_dir}

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitelib}/%{name}*
%attr(0755, root, root) %{_bindir}/%{name}

%changelog
* %(date "+%a %b %d %Y") %{name} - %{version}-%{release}
- Automatic build
