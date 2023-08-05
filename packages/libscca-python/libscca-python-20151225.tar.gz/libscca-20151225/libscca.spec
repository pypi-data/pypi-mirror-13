Name: libscca
Version: 20151225
Release: 1
Summary: Library to access the Windows Prefetch File (PF) format
Group: System Environment/Libraries
License: LGPL
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libscca/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
                
                

%description
libscca is a library to access the Windows Prefetch File (PF) format

%package devel
Summary: Header files and libraries for developing applications for libscca
Group: Development/Libraries
Requires: libscca = %{version}-%{release}

%description devel
Header files and libraries for developing applications for libscca.

%package tools
Summary: Several tools for accessing Windows Prefetch files
Group: Applications/System
Requires: libscca = %{version}-%{release}

%description tools
Several tools for accessing Windows Prefetch files

%package python
Summary: Python bindings for libscca
Group: System Environment/Libraries
Requires: libscca = %{version}-%{release} python
BuildRequires: python-devel

%description python
Python bindings for libscca

%prep
%setup -q

%build
%configure --prefix=/usr --libdir=%{_libdir} --mandir=%{_mandir} --enable-python
make %{?_smp_mflags}

%install
rm -rf ${RPM_BUILD_ROOT}
make DESTDIR=${RPM_BUILD_ROOT} install

%clean
rm -rf ${RPM_BUILD_ROOT}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%attr(755,root,root) %{_libdir}/*.so.*

%files devel
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README ChangeLog
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so
%{_libdir}/pkgconfig/libscca.pc
%{_includedir}/*
%{_mandir}/man3/*

%files tools
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%attr(755,root,root) %{_bindir}/sccainfo
%{_mandir}/man1/*

%files python
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%{_libdir}/python*/site-packages/*.a
%{_libdir}/python*/site-packages/*.la
%{_libdir}/python*/site-packages/*.so

%changelog
* Fri Dec 25 2015 Joachim Metz <joachim.metz@gmail.com> 20151225-1
- Auto-generated

