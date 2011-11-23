try:
    from kvmtools.qemu_kvm_options import qemu_kvm_options
except ImportError:
    import os
    os.system("generate-kvm-options --generate")
    try:
        from kvmtools.qemu_kvm_options import qemu_kvm_options
    except ImportError, error_msg:
        import sys
        print error_msg
        sys.extit(1)
        


