===
KVM
===

.. todo:: Some of this is installation guide material and should probably be
     moved.

KVM is configured as the default hypervisor for Compute.

.. note::

   This document contains several sections about hypervisor selection.  If you
   are reading this document linearly, you do not want to load the KVM module
   before you install ``nova-compute``.  The ``nova-compute`` service depends
   on qemu-kvm, which installs ``/lib/udev/rules.d/45-qemu-kvm.rules``, which
   sets the correct permissions on the ``/dev/kvm`` device node.

To enable KVM explicitly, add the following configuration options to the
``/etc/nova/nova.conf`` file:

.. code-block:: ini

   compute_driver = libvirt.LibvirtDriver

   [libvirt]
   virt_type = kvm

The KVM hypervisor supports the following virtual machine image formats:

* Raw
* QEMU Copy-on-write (QCOW2)
* QED Qemu Enhanced Disk
* VMware virtual machine disk format (vmdk)

This section describes how to enable KVM on your system.  For more information,
see the following distribution-specific documentation:

* `Fedora: Virtualization Getting Started Guide <http://docs.fedoraproject.org/
  en-US/Fedora/22/html/Virtualization_Getting_Started_Guide/index.html>`_
  from the Fedora 22 documentation.
* `Ubuntu: KVM/Installation <https://help.ubuntu.com/community/KVM/
  Installation>`_ from the Community Ubuntu documentation.
* `Debian: Virtualization with KVM <http://static.debian-handbook.info/browse/
  stable/sect.virtualization.html#idp11279352>`_ from the Debian handbook.
* `Red Hat Enterprise Linux: Installing virtualization packages on an existing
  Red Hat Enterprise Linux system <http://docs.redhat.com/docs/en-US/
  Red_Hat_Enterprise_Linux/6/html/Virtualization_Host_Configuration_and_Guest_
  Installation_Guide/sect-Virtualization_Host_Configuration_and_Guest_Installa
  tion_Guide-Host_Installation-Installing_KVM_packages_on_an_existing_Red_Hat_
  Enterprise_Linux_system.html>`_ from the ``Red Hat Enterprise Linux
  Virtualization Host Configuration and Guest Installation Guide``.
* `openSUSE: Installing KVM <http://doc.opensuse.org/documentation/html/
  openSUSE/opensuse-kvm/cha.kvm.requires.html#sec.kvm.requires.install>`_
  from the openSUSE Virtualization with KVM manual.
* `SLES: Installing KVM <https://www.suse.com/documentation/sles-12/book_virt/
  data/sec_vt_installation_kvm.html>`_ from the SUSE Linux Enterprise Server
  ``Virtualization Guide``.

.. _enable-kvm:

Enable KVM
~~~~~~~~~~

The following sections outline how to enable KVM based hardware virtualization
on different architectures and platforms.  To perform these steps, you must be
logged in as the ``root`` user.

For x86 based systems
---------------------

#. To determine whether the ``svm`` or ``vmx`` CPU extensions are present, run
   this command:

   .. code-block:: console

      # grep -E 'svm|vmx' /proc/cpuinfo

   This command generates output if the CPU is capable of
   hardware-virtualization. Even if output is shown, you might still need to
   enable virtualization in the system BIOS for full support.

   If no output appears, consult your system documentation to ensure that your
   CPU and motherboard support hardware virtualization.  Verify that any
   relevant hardware virtualization options are enabled in the system BIOS.

   The BIOS for each manufacturer is different. If you must enable
   virtualization in the BIOS, look for an option containing the words
   ``virtualization``, ``VT``, ``VMX``, or ``SVM``.

#. To list the loaded kernel modules and verify that the ``kvm`` modules are
   loaded, run this command:

   .. code-block:: console

      # lsmod | grep kvm

   If the output includes ``kvm_intel`` or ``kvm_amd``, the ``kvm`` hardware
   virtualization modules are loaded and your kernel meets the module
   requirements for OpenStack Compute.

   If the output does not show that the ``kvm`` module is loaded, run this
   command to load it:

   .. code-block:: console

      # modprobe -a kvm

   Run the command for your CPU. For Intel, run this command:

   .. code-block:: console

      # modprobe -a kvm-intel

   For AMD, run this command:

   .. code-block:: console

      # modprobe -a kvm-amd

   Because a KVM installation can change user group membership, you might need
   to log in again for changes to take effect.

   If the kernel modules do not load automatically, use the procedures listed
   in these subsections.

If the checks indicate that required hardware virtualization support or kernel
modules are disabled or unavailable, you must either enable this support on the
system or find a system with this support.

.. note::

   Some systems require that you enable VT support in the system BIOS.  If you
   believe your processor supports hardware acceleration but the previous
   command did not produce output, reboot your machine, enter the system BIOS,
   and enable the VT option.

If KVM acceleration is not supported, configure Compute to use a different
hypervisor, such as :ref:`QEMU <compute_qemu>`.

These procedures help you load the kernel modules for Intel-based and AMD-based
processors if they do not load automatically during KVM installation.

.. rubric:: Intel-based processors

If your compute host is Intel-based, run these commands as root to load the
kernel modules:

.. code-block:: console

   # modprobe kvm
   # modprobe kvm-intel

Add these lines to the ``/etc/modules`` file so that these modules load on
reboot:

.. code-block:: console

   kvm
   kvm-intel

.. rubric:: AMD-based processors

If your compute host is AMD-based, run these commands as root to load the
kernel modules:

.. code-block:: console

   # modprobe kvm
   # modprobe kvm-amd

Add these lines to ``/etc/modules`` file so that these modules load on reboot:

.. code-block:: console

   kvm
   kvm-amd

For POWER based systems
-----------------------

KVM as a hypervisor is supported on POWER system's PowerNV platform.

#. To determine if your POWER platform supports KVM based virtualization run
   the following command:

   .. code-block:: console

      # cat /proc/cpuinfo | grep PowerNV

   If the previous command generates the following output, then CPU supports
   KVM based virtualization.

   .. code-block:: console

      platform: PowerNV

   If no output is displayed, then your POWER platform does not support KVM
   based hardware virtualization.

#. To list the loaded kernel modules and verify that the ``kvm`` modules are
   loaded, run the following command:

   .. code-block:: console

      # lsmod | grep kvm

   If the output includes ``kvm_hv``, the ``kvm`` hardware virtualization
   modules are loaded and your kernel meets the module requirements for
   OpenStack Compute.

   If the output does not show that the ``kvm`` module is loaded, run the
   following command to load it:

   .. code-block:: console

      # modprobe -a kvm

   For PowerNV platform, run the following command:

   .. code-block:: console

      # modprobe -a kvm-hv

   Because a KVM installation can change user group membership, you might need
   to log in again for changes to take effect.

Configure Compute backing storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Backing Storage is the storage used to provide the expanded operating system
image, and any ephemeral storage. Inside the virtual machine, this is normally
presented as two virtual hard disks (for example, ``/dev/vda`` and ``/dev/vdb``
respectively). However, inside OpenStack, this can be derived from one of these
methods: ``lvm``, ``qcow``, ``rbd`` or ``flat``, chosen using the
:oslo.config:option:`libvirt.images_type` option in ``nova.conf`` on the
compute node.

.. note::

   The option ``raw`` is acceptable but deprecated in favor of ``flat``.  The
   Flat back end uses either raw or QCOW2 storage. It never uses a backing
   store, so when using QCOW2 it copies an image rather than creating an
   overlay. By default, it creates raw files but will use QCOW2 when creating a
   disk from a QCOW2 if :oslo.config:option:`force_raw_images` is not set in
   configuration.

QCOW is the default backing store. It uses a copy-on-write philosophy to delay
allocation of storage until it is actually needed. This means that the space
required for the backing of an image can be significantly less on the real disk
than what seems available in the virtual machine operating system.

Flat creates files without any sort of file formatting, effectively creating
files with the plain binary one would normally see on a real disk. This can
increase performance, but means that the entire size of the virtual disk is
reserved on the physical disk.

Local `LVM volumes
<https://en.wikipedia.org/wiki/Logical_Volume_Manager_(Linux)>`__ can also be
used. Set the :oslo.config:option:`libvirt.images_volume_group` configuration
option to the name of the LVM group you have created.

Direct download of images from Ceph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the Glance image service is set up with the Ceph backend and Nova is using
a local ephemeral store (``[libvirt]/images_type!=rbd``), it is possible to
configure Nova to download images directly into the local compute image cache.

With the following configuration, images are downloaded using the RBD export
command instead of using the Glance HTTP API. In some situations, especially
for very large images, this could be substantially faster and can improve the
boot times of instances.

On the Glance API node in ``glance-api.conf``:

.. code-block:: ini

   [DEFAULT]
   show_image_direct_url=true

On the Nova compute node in nova.conf:

.. code-block:: ini

   [glance]
   enable_rbd_download=true
   rbd_user=glance
   rbd_pool=images
   rbd_ceph_conf=/etc/ceph/ceph.conf
   rbd_connect_timeout=5

Specify the CPU model of KVM guests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Compute service enables you to control the guest CPU model that is exposed
to KVM virtual machines. Use cases include:

* To maximize performance of virtual machines by exposing new host CPU features
  to the guest

* To ensure a consistent default CPU across all machines, removing reliance of
  variable QEMU defaults

In libvirt, the CPU is specified by providing a base CPU model name (which is a
shorthand for a set of feature flags), a set of additional feature flags, and
the topology (sockets/cores/threads). The libvirt KVM driver provides a number
of standard CPU model names. These models are defined in the
``/usr/share/libvirt/cpu_map.xml`` file for libvirt prior to version 4.7.0 or
``/usr/share/libvirt/cpu_map/*.xml`` files thereafter. Make a check to
determine which models are supported by your local installation.

Two Compute configuration options in the :oslo.config:group:`libvirt` group
of ``nova.conf`` define which type of CPU model is exposed to the hypervisor
when using KVM: :oslo.config:option:`libvirt.cpu_mode` and
:oslo.config:option:`libvirt.cpu_models`.

The :oslo.config:option:`libvirt.cpu_mode` option can take one of the following
values: ``none``, ``host-passthrough``, ``host-model``, and ``custom``.

See `Effective Virtual CPU configuration in Nova`_ for a recorded presentation
about this topic.

.. _Effective Virtual CPU configuration in Nova: https://www.openstack.org/videos/summits/berlin-2018/effective-virtual-cpu-configuration-in-nova

Host model (default for KVM & QEMU)
-----------------------------------

If your ``nova.conf`` file contains ``cpu_mode=host-model``, libvirt identifies
the CPU model in ``/usr/share/libvirt/cpu_map.xml`` for version prior to 4.7.0
or ``/usr/share/libvirt/cpu_map/*.xml`` for version 4.7.0 and higher that most
closely matches the host, and requests additional CPU flags to complete the
match. This configuration provides the maximum functionality and performance
and maintains good reliability.

With regard to enabling and facilitating live migration between
compute nodes, you should assess whether ``host-model`` is suitable
for your compute architecture. In general, using ``host-model`` is a
safe choice if your compute node CPUs are largely identical. However,
if your compute nodes span multiple processor generations, you may be
better advised to select a ``custom`` CPU model.

Host pass through
-----------------

If your ``nova.conf`` file contains ``cpu_mode=host-passthrough``, libvirt
tells KVM to pass through the host CPU with no modifications.  The difference
to host-model, instead of just matching feature flags, every last detail of the
host CPU is matched. This gives the best performance, and can be important to
some apps which check low level CPU details, but it comes at a cost with
respect to migration.

In ``host-passthrough`` mode, the guest can only be live-migrated to a
target host that matches the source host extremely closely. This
definitely includes the physical CPU model and running microcode, and
may even include the running kernel. Use this mode only if

* your compute nodes have a very large degree of homogeneity
  (i.e. substantially all of your compute nodes use the exact same CPU
  generation and model), and you make sure to only live-migrate
  between hosts with exactly matching kernel versions, *or*

* you decide, for some reason and against established best practices,
  that your compute infrastructure should not support any live
  migration at all.

Custom
------

If :file:`nova.conf` contains :oslo.config:option:`libvirt.cpu_mode`\ =custom,
you can explicitly specify an ordered list of supported named models using
the :oslo.config:option:`libvirt.cpu_models` configuration option. It is
expected that the list is ordered so that the more common and less advanced cpu
models are listed earlier.

An end user can specify required CPU features through traits. When specified,
the libvirt driver will select the first cpu model in the
:oslo.config:option:`libvirt.cpu_models` list that can provide the requested
feature traits. If no CPU feature traits are specified then the instance will
be configured with the first cpu model in the list.

For example, if specifying CPU features ``avx`` and ``avx2`` as follows:

.. code-block:: console

    $ openstack flavor set FLAVOR_ID --property trait:HW_CPU_X86_AVX=required \
                                     --property trait:HW_CPU_X86_AVX2=required

and :oslo.config:option:`libvirt.cpu_models` is configured like this:

.. code-block:: ini

    [libvirt]
    cpu_mode = custom
    cpu_models = Penryn,IvyBridge,Haswell,Broadwell,Skylake-Client

Then ``Haswell``, the first cpu model supporting both ``avx`` and ``avx2``,
will be chosen by libvirt.

In selecting the ``custom`` mode, along with a
:oslo.config:option:`libvirt.cpu_models` that matches the oldest of your compute
node CPUs, you can ensure that live migration between compute nodes will always
be possible. However, you should ensure that the
:oslo.config:option:`libvirt.cpu_models` you select passes the correct CPU
feature flags to the guest.

If you need to further tweak your CPU feature flags in the ``custom``
mode, see `Set CPU feature flags`_.

.. note::

  If :oslo.config:option:`libvirt.cpu_models` is configured,
  the CPU models in the list needs to be compatible with the host CPU. Also, if
  :oslo.config:option:`libvirt.cpu_model_extra_flags` is configured, all flags
  needs to be compatible with the host CPU. If incompatible CPU models or flags
  are specified, nova service will raise an error and fail to start.


None (default for all libvirt-driven hypervisors other than KVM & QEMU)
-----------------------------------------------------------------------

If your ``nova.conf`` file contains ``cpu_mode=none``, libvirt does not specify
a CPU model. Instead, the hypervisor chooses the default model.

Set CPU feature flags
~~~~~~~~~~~~~~~~~~~~~

Regardless of whether your selected :oslo.config:option:`libvirt.cpu_mode` is
``host-passthrough``, ``host-model``, or ``custom``, it is also
possible to selectively enable additional feature flags. Suppose your
selected ``custom`` CPU model is ``IvyBridge``, which normally does
not enable the ``pcid`` feature flag --- but you do want to pass
``pcid`` into your guest instances. In that case, you would set:

.. code-block:: ini

   [libvirt]
   cpu_mode = custom
   cpu_models = IvyBridge
   cpu_model_extra_flags = pcid

Nested guest support
~~~~~~~~~~~~~~~~~~~~

You may choose to enable support for nested guests --- that is, allow
your Nova instances to themselves run hardware-accelerated virtual
machines with KVM. Doing so requires a module parameter on
your KVM kernel module, and corresponding ``nova.conf`` settings.

Nested guest support in the KVM kernel module
---------------------------------------------

To enable nested KVM guests, your compute node must load the
``kvm_intel`` or ``kvm_amd`` module with ``nested=1``. You can enable
the ``nested`` parameter permanently, by creating a file named
``/etc/modprobe.d/kvm.conf`` and populating it with the following
content:

.. code-block:: none

   options kvm_intel nested=1
   options kvm_amd nested=1

A reboot may be required for the change to become effective.

Nested guest support in ``nova.conf``
-------------------------------------

To support nested guests, you must set your
:oslo.config:option:`libvirt.cpu_mode` configuration to one of the following
options:

Host pass through
  In this mode, nested virtualization is automatically enabled once
  the KVM kernel module is loaded with nesting support.

  .. code-block:: ini

     [libvirt]
     cpu_mode = host-passthrough

  However, do consider the other implications that `Host pass
  through`_ mode has on compute functionality.

Host model
  In this mode, nested virtualization is automatically enabled once
  the KVM kernel module is loaded with nesting support, **if** the
  matching CPU model exposes the ``vmx`` feature flag to guests by
  default (you can verify this with ``virsh capabilities`` on your
  compute node). If your CPU model does not pass in the ``vmx`` flag,
  you can force it with :oslo.config:option:`libvirt.cpu_model_extra_flags`:

  .. code-block:: ini

     [libvirt]
     cpu_mode = host-model
     cpu_model_extra_flags = vmx

  Again, consider the other implications that apply to the `Host model
  (default for KVM & Qemu)`_ mode.

Custom
  In custom mode, the same considerations apply as in host-model mode,
  but you may *additionally* want to ensure that libvirt passes not only
  the ``vmx``, but also the ``pcid`` flag to its guests:

  .. code-block:: ini

     [libvirt]
     cpu_mode = custom
     cpu_models = IvyBridge
     cpu_model_extra_flags = vmx,pcid

Nested guest support limitations
--------------------------------

When enabling nested guests, you should be aware of (and inform your
users about) certain limitations that are currently inherent to nested
KVM virtualization. Most importantly, guests using nested
virtualization will, *while nested guests are running*,

* fail to complete live migration;
* fail to resume from suspend.

See `the KVM documentation
<https://www.linux-kvm.org/page/Nested_Guests#Limitations>`_ for more
information on these limitations.

Guest agent support
~~~~~~~~~~~~~~~~~~~

Use guest agents to enable optional access between compute nodes and guests
through a socket, using the QMP protocol.

To enable this feature, you must set ``hw_qemu_guest_agent=yes`` as a metadata
parameter on the image you wish to use to create the guest-agent-capable
instances from. You can explicitly disable the feature by setting
``hw_qemu_guest_agent=no`` in the image metadata.

KVM performance tweaks
~~~~~~~~~~~~~~~~~~~~~~

The `VHostNet <http://www.linux-kvm.org/page/VhostNet>`_ kernel module improves
network performance. To load the kernel module, run the following command as
root:

.. code-block:: console

   # modprobe vhost_net

Troubleshoot KVM
~~~~~~~~~~~~~~~~

Trying to launch a new virtual machine instance fails with the ``ERROR`` state,
and the following error appears in the ``/var/log/nova/nova-compute.log`` file:

.. code-block:: console

   libvirtError: internal error no supported architecture for os type 'hvm'

This message indicates that the KVM kernel modules were not loaded.

If you cannot start VMs after installation without rebooting, the permissions
might not be set correctly. This can happen if you load the KVM module before
you install ``nova-compute``.  To check whether the group is set to ``kvm``,
run:

.. code-block:: console

   # ls -l /dev/kvm

If it is not set to ``kvm``, run:

.. code-block:: console

   # udevadm trigger
