#!/usr/bin/env python3
parser.add_argument('--dry-run', action='store_true', help='Dont remove, just print')
parser.add_argument('--force', action='store_true', help='Force (bypass some safety checks)')
parser.add_argument('--log', default=config.get('log', DEFAULT_LOG))
parser.add_argument('--verbose', action='store_true')
parser.add_argument('--health', action='store_true', help='Show health and exit')


args = parser.parse_args()


if args.health:
kernels = get_installed_kernel_core_packages()
running = get_running_uname()
print(f"Running kernel: {running}")
print(f"Installed kernel-core packages: {len(kernels)}")
if len(kernels) > args.keep:
print(f"You have {len(kernels) - args.keep} candidate kernel(s) to remove")
else:
print("Kernel count within configured limit")
try:
out = run("dnf repoquery --unneeded || true")
orphans = [l for l in out.splitlines() if l.strip()]
print(f"Orphaned packages: {len(orphans)}")
except Exception:
print("Orphan detection unavailable (repoquery failed)")
sys.exit(0)


kernels = get_installed_kernel_core_packages()
if not kernels:
print("No kernel-core packages found; exiting")
sys.exit(0)


running = get_running_uname()
keep_list = kernels[:args.keep]
old_candidates = kernels[args.keep:]


if args.verbose:
print("Keeping:")
for k in keep_list: print(' ', k)
print('Candidates:')
for k in old_candidates: print(' ', k)


removals: list[str] = []
for pkg in old_candidates:
vr = pkg_version_from_kernel_core(pkg)
if vr:
removals.extend(find_packages_for_version(vr))


removals = sorted(set(removals))


# Safety: do not remove running kernel unless forced
if not args.force:
removals = [r for r in removals if running not in r]


if not removals:
print('Nothing to remove after safety checks')
append_log('Nothing to remove', args.log)
notify('DNF AutoClean', 'Nothing to remove')
sys.exit(0)


print('Packages scheduled for removal:')
for r in removals: print(' ', r)


append_log(f'Planned removals: {removals}', args.log)


if args.dry_run:
print('[DRY RUN] No packages removed')
notify('DNF AutoClean (dry-run)', f'{len(removals)} packages would be removed')
sys.exit(0)


# execute
try:
dnf_remove(removals, dry_run=False)
dnf_autoremove(dry_run=False)
append_log(f'Removed {len(removals)} packages + orphans', args.log)
notify('DNF AutoClean', f'Removed {len(removals)} packages + orphans')
except Exception as e:
append_log(f'Removal failed: {e}', args.log)
notify('DNF AutoClean (failed)', str(e))
print('Removal failed:', e)
sys.exit(1)




if __name__ == '__main__':
main()
