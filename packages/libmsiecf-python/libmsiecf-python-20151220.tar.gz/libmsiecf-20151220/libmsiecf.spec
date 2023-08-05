Name: libmsiecf
Version: 20151220
Release: 1
Summary: Library to access the MSIE Cache File (index.dat) format.
Group: System Environment/Libraries
License: LGPL
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libmsiecf/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
             
               

%description
libmsiecf is a library to access the MSIE Cache File (index.dat) format.

%package devel
Summary: Header files and libraries for developing applications for libmsiecf
Group: Development/Libraries
Requires: libmsiecf = %{version}-%{release}

%description devel
Header files and libraries for developing applications for libmsiecf.

%package tools
Summary: Several tools for reading MSIE Cache File (index.dat).
Group: Applications/System
Requires: libmsiecf = %{version}-%{release} 
 

%description tools
Several tools for reading MSIE Cache File (index.dat).

%package python
Summary: Python bindings for libmsiecf
Group: System Environment/Libraries
Requires: libmsiecf = %{version}-%{release} python
BuildRequires: python-devel

%description python
Python bindings for libmsiecf

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
%{_libdir}/pkgconfig/libmsiecf.pc
%{_includedir}/*
%{_mandir}/man3/*

%files tools
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%attr(755,root,root) %{_bindir}/msiecfexport
%attr(755,root,root) %{_bindir}/msiecfinfo
%{_mandir}/man1/*

%files python
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%{_libdir}/python*/site-packages/*.a
%{_libdir}/python*/site-packages/*.la
%{_libdir}/python*/site-packages/*.so

%changelog
* Sun Dec 20 2015 Joachim Metz <joachim.metz@gmail.com> 20151220-1
- Auto-generated

