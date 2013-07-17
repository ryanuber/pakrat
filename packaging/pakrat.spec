%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%define pakrat_dir %(tar -tzf %{SOURCE0} | egrep '^(\./)?pakrat(-[^/]*)?/$')

name: pakrat
summary: A Python library for mirroring and versioning YUM repositories
version: 0.0.7
release: 1%{?dist}
buildarch: noarch
license: MIT
source0: %{name}.tar.gz
requires: yum
requires: createrepo

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

%install
%{__mkdir_p} %{buildroot}/%{python_sitelib}/%{name} %{buildroot}/%{_bindir}
%{__cp} %{name}/*.py %{buildroot}/%{python_sitelib}/%{name}
%{__cp} bin/%{name} %{buildroot}/%{_bindir}

%clean
rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
%dir %{python_sitelib}/%{name}
%{python_sitelib}/%{name}/*.py
%attr(0755, root, root) %{_bindir}/%{name}

%changelog
* %(date "+%a %b %d %Y") %{name} - %{version}-%{release}
- Automatic build
