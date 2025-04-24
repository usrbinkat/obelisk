# Docker Infrastructure Reorganization Cleanup Plan

## CRITICAL INSTRUCTION

**IMPORTANT: WE CANNOT DELETE ANY FILES UNLESS we very carefully confirm that all code, features, and functionality are fully reproduced in the new locations where the code was relocated during restructuring. It is IMPERATIVE that there be NO regressions, bugs, or feature loss when we commit this as a PR.**

Each file must be individually verified for:
1. Complete functionality preservation
2. No subtle differences in behavior
3. All dependent code properly updated to reference new locations
4. Comprehensive testing of all affected features

**Zero tolerance for feature regression.** When in doubt, keep both versions until verification is absolutely certain.

---

This plan outlines the files that need to be removed or replaced after the Docker infrastructure reorganization to maintain a clean and consistent codebase.

## Files Moved to New Location

| Original File | New Location | Status | Action |
|---------------|--------------|--------|--------|
| `/Dockerfile` | `/deployments/docker/images/core/Dockerfile` | Duplicated | Remove original after testing |
| `/Dockerfile.rag` | `/deployments/docker/images/rag/Dockerfile` | Duplicated | Remove original after testing |
| `/Dockerfile.init` | `/deployments/docker/images/init/Dockerfile` | Duplicated | Remove original after testing |
| `/docker-entrypoint.sh` | Not yet moved | To be moved | Move to appropriate location |
| `/docker/init-scripts/configure-services.sh` | `/deployments/docker/images/init/scripts/configure-services.sh` | Duplicated | Remove original directory after testing |
| `/docker/init-scripts/download-models.sh` | `/deployments/docker/images/init/scripts/download-models.sh` | Duplicated | Remove original directory after testing |
| `/docker/init-scripts/generate-tokens.sh` | `/deployments/docker/images/init/scripts/generate-tokens.sh` | Duplicated | Remove original directory after testing |
| `/docker/init-scripts/init-sequence.sh` | `/deployments/docker/images/init/scripts/init-sequence.sh` | Duplicated | Remove original directory after testing |
| `/docker-compose.yaml` | `/deployments/docker/compose/dev.yaml` | Functionally replaced | Remove original after testing |
| `/litellm-config.yaml` | `/deployments/docker/config/litellm_config.yaml` | Duplicated | Remove original after testing |

## Cleanup Steps

### 1. Rigorous Verification Process (Required Before ANY Removal)

For each file planned for removal:

- **Line-by-line comparison**: Carefully compare source and destination files to ensure identical functionality
  - Use `diff -u <original_file> <new_file>` to identify any differences
  - Document and understand every difference, no matter how small
  - Verify that differences are intentional improvements, not accidental changes

- **File reference tracking**: Identify ALL references to the original file
  - Use `grep -r "<original_file_name>" --include="*.py" --include="*.sh" --include="*.yaml" .` 
  - Track down each reference and ensure it's updated or appropriately handled

- **Feature matrix validation**: Create a checklist of all features that depend on each file
  - Test each feature with both original and new file locations
  - Document test results in detail
  - Retain both files if ANY test fails or behaves differently

- **Environment variable testing**: Test with various environment configurations
  - Test default settings
  - Test with custom settings
  - Test with missing/invalid settings to verify error handling

- **Edge case testing**: Test unusual scenarios that might reveal subtle differences
  - Resource constraints
  - High load conditions
  - Recovery from failures

### 2. Prepare for Removal (Only After Verification)

- Verify all Docker services work with the new structure
  - Run `task docker-config` to validate configuration
  - Run `task docker` to start services
  - Run `task docker-test` to validate functionality
  - Verify all key features are working correctly

- Check for references to old files
  - Search for hardcoded paths to removed files
  - Update references to point to new locations
  - Validate updated references

### 2. File Removal PR

Create a PR with the following changes:

```bash
# Remove original Dockerfiles
git rm Dockerfile
git rm Dockerfile.rag
git rm Dockerfile.init

# Remove original docker-compose file
git rm docker-compose.yaml

# Remove original litellm config
git rm litellm-config.yaml

# Remove original init scripts directory
git rm -r docker/init-scripts/

# Document the removals in a commit message
git commit -m "cleanup(docker): remove original Docker files after reorganization

- Remove root Dockerfiles now located in deployments/docker/images/
- Remove docker-compose.yaml now replaced by deployments/docker/compose/dev.yaml
- Remove litellm-config.yaml now located in deployments/docker/config/
- Remove docker/init-scripts/ now located in deployments/docker/images/init/scripts/

This cleanup follows the Docker infrastructure reorganization that moved
these files to a more structured layout under the deployments directory."
```

### 3. Entrypoint File Handling

For `docker-entrypoint.sh`, we have two options:

1. **Option A**: Move to core image directory
   ```bash
   # Create a copy in the new location
   cp docker-entrypoint.sh deployments/docker/images/core/entrypoint.sh
   
   # Remove the original after testing
   git rm docker-entrypoint.sh
   ```

2. **Option B**: If it contains shared functionality, refactor and move
   ```bash
   # Create appropriate versions in service directories
   # Update Dockerfiles to reference the new locations
   # Remove the original after testing
   git rm docker-entrypoint.sh
   ```

### 4. Update Documentation

- Update README.md to point to new file locations
- Update any references in documentation files
- Update CI/CD pipelines if they reference the old files

## Future Improvements

1. **Move docker-entrypoint.sh**: Complete this move in a separate PR after evaluating its usage.
   
2. **Organize /hack/ Directory**: Consider moving utility scripts from `/hack/` to `/scripts/` or other appropriate locations in a future restructuring phase.

3. **Consolidate Remaining Docker-Related Files**: Identify any other Docker-related files that may not have been caught in this reorganization and move them to appropriate locations.

## Final Validation

Before merging the cleanup PR:

1. **Complete feature test matrix**: Create and execute a comprehensive test matrix covering all affected functionality
   - Document test cases, expected results, and actual results
   - Include normal operation, boundary conditions, and error cases
   - Have independent verification by multiple team members

2. **CI/CD pipeline validation**: Run complete CI/CD pipeline multiple times
   - Ensure all automated tests pass consistently
   - Verify build artifacts are identical to those produced with original files

3. **Canary deployment**: If possible, deploy changes to a staging environment
   - Run the system with real workloads
   - Monitor for any deviations in behavior, performance, or error rates

4. **Rollback plan**: Prepare and document a detailed rollback plan
   - Ensure ability to quickly revert if any issues are discovered after merge
   - Test the rollback procedure to confirm it works

5. **Documentation review**: Complete review of all documentation
   - Ensure all references to file locations are accurate
   - Update any examples or tutorials that reference the old structure

## Timeline and Verification Checklist

Each file removal must be:
1. ⬜ Individually verified with direct comparison
2. ⬜ Tested in isolation to confirm behavior preservation
3. ⬜ Tested in integration to verify system-wide behavior
4. ⬜ Reviewed by at least one additional team member
5. ⬜ Documented with evidence of successful verification

Only after ALL files pass these checks should the cleanup PR be created.

**No timeline pressure**: This verification process takes priority over any schedule considerations. We will only remove files when we are 100% confident that doing so will cause no regressions.