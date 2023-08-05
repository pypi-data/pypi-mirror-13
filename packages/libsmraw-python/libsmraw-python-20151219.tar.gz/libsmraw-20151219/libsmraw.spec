Name: libsmraw
Version: 20151219
Release: 1
Summary: Library to access the storage media (SM) (split) RAW format
Group: System Environment/Libraries
License: LGPL
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libsmraw/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
              
              

%description
libsmraw is library to access the storage media (SM) (split) RAW format
The library supports both RAW and split RAW.

%package devel
Summary: Header files and libraries for developing applications for libsmraw
Group: Development/Libraries
Requires: libsmraw = %{version}-%{release}

%description devel
Header files and libraries for developing applications for libsmraw.

%package tools
Summary: Several tools for reading and writing storage media (SM) (split) RAW files
Group: Applications/System
Requires: libsmraw = %{version}-%{release} openssl  fuse-libs 
BuildRequires: openssl-devel  fuse-devel 

%description tools
Several tools for reading and writing storage media (SM) (split) RAW files.
It contains tools to acquire, export, query and verify storage media (SM) (split) RAW files.

%package python
Summary: Python bindings for libsmraw
Group: System Environment/Libraries
Requires: libsmraw = %{version}-%{release} python
BuildRequires: python-devel

%description python
Python bindings for libsmraw

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
%{_libdir}/pkgconfig/libsmraw.pc
%{_includedir}/*
%{_mandir}/man3/*

%files tools
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%attr(755,root,root) %{_bindir}/smrawmount
%attr(755,root,root) %{_bindir}/smrawverify
%{_mandir}/man1/*

%files python
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS README
%{_libdir}/python*/site-packages/*.a
%{_libdir}/python*/site-packages/*.la
%{_libdir}/python*/site-packages/*.so

%changelog
* Sat Dec 19 2015 Joachim Metz <joachim.metz@gmail.com> 20151219-1
- Auto-generated

