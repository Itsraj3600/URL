import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow login page without authentication
  if (pathname === '/admin/login') {
    return NextResponse.next();
  }

  // Protect dashboard routes
  if (pathname.startsWith('/admin/dashboard')) {
    const token = request.cookies.get('auth_token')?.value;

    if (!token) {
      return NextResponse.redirect(new URL('/admin/login', request.url));
    }

    // Verify token (simple validation - extend with full JWT verification)
    try {
      const response = await fetch(new URL('/api/admin/verify', request.url).toString(), {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        return NextResponse.redirect(new URL('/admin/login', request.url));
      }
    } catch (error) {
      return NextResponse.redirect(new URL('/admin/login', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/admin/:path*'],
};
