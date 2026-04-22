/**
 * Authentication utilities using Clerk
 * Replaces MetaMask wallet authentication
 * Supports multiple roles per user (patient, doctor, or both)
 */

export function getUserId(clerkUserId: string): string {
    // Use Clerk user ID as the unique identifier
    return clerkUserId;
}

export function getUserRoles(user: any): ('patient' | 'doctor')[] {
    const roles = user?.unsafeMetadata?.roles;
    
    // Handle legacy single role format
    if (!roles && user?.unsafeMetadata?.role) {
        return [user.unsafeMetadata.role as 'patient' | 'doctor'];
    }
    
    return Array.isArray(roles) ? roles : [];
}

export function hasRole(user: any, role: 'patient' | 'doctor'): boolean {
    return getUserRoles(user).includes(role);
}

export function isPatient(user: any): boolean {
    return hasRole(user, 'patient');
}

export function isDoctor(user: any): boolean {
    return hasRole(user, 'doctor');
}

export function hasAnyRole(user: any): boolean {
    return getUserRoles(user).length > 0;
}

export function getActiveRole(user: any): 'patient' | 'doctor' | null {
    // Check for explicitly set active role
    const activeRole = user?.unsafeMetadata?.activeRole;
    if (activeRole && hasRole(user, activeRole)) {
        return activeRole;
    }
    
    // Default to first available role
    const roles = getUserRoles(user);
    return roles.length > 0 ? roles[0] : null;
}

export function setActiveRole(user: any, role: 'patient' | 'doctor'): Promise<any> {
    if (!hasRole(user, role)) {
        throw new Error(`User does not have ${role} role`);
    }
    
    return user.update({
        unsafeMetadata: {
            ...user.unsafeMetadata,
            activeRole: role
        }
    });
}
