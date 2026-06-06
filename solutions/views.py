from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SolutionBookingForm, SolutionRescheduleForm
from .models import SolutionBooking


SOLUTION_SERVICES = [
    {
        'slug': 'website-development',
        'title': 'Website Development',
        'summary': 'Business websites that are fast, clear, and conversion-focused.',
        'overview': 'We build modern websites for startups, educational institutions, and local businesses with responsive design and performance-first delivery.',
        'ideal_for': 'Small businesses, institutions, professionals, and local brands.',
        'timeline': '5 to 15 working days depending on scope.',
        'icon_sprite': 'website-development',
        'feature_cards': [
            {'title': 'UI Design', 'description': 'Brand-aligned layouts designed for clarity and conversion.', 'icon_sprite': 'ui-ux-design'},
            {'title': 'Responsive Build', 'description': 'Mobile-first implementation for all devices.', 'icon_sprite': 'website-development'},
            {'title': 'SEO Basics', 'description': 'Core metadata and on-page optimization setup.', 'icon_sprite': 'content-seo-support'},
        ],
        'included_points': [
            {'title': 'Pages Setup', 'text': 'Essential pages including home, about, services, and contact.'},
            {'title': 'Deployment', 'text': 'Live deployment support with domain/DNS guidance.'},
            {'title': 'Handover', 'text': 'Source handover and admin usage walkthrough.'},
        ],
        'pricing_note': 'Pricing depends on page count and features.',
        'tagline': 'Launch quickly with a clean and reliable web presence.',
    },
    {
        'slug': 'web-application-development',
        'title': 'Web Application Development',
        'summary': 'Custom workflow apps for operations, bookings, and dashboards.',
        'overview': 'From requirement analysis to delivery, we build secure web applications with role-based access and scalable architecture.',
        'ideal_for': 'Teams needing custom workflows, automation, and dashboards.',
        'timeline': '2 to 8 weeks based on modules and integrations.',
        'icon_sprite': 'web-application-development',
        'feature_cards': [
            {'title': 'Custom Modules', 'description': 'Features tailored to your internal process.', 'icon_sprite': 'web-application-development'},
            {'title': 'Role Access', 'description': 'Permissions for admin, staff, and end users.', 'icon_sprite': 'process-flow'},
            {'title': 'Reports', 'description': 'Operational dashboards and export-ready reports.', 'icon_sprite': 'content-seo-support'},
        ],
        'included_points': [
            {'title': 'Requirement Mapping', 'text': 'Detailed scope planning and sprint structure.'},
            {'title': 'Testing', 'text': 'Functional and UX testing before launch.'},
            {'title': 'Support', 'text': 'Post-launch bug fixes and enhancements support.'},
        ],
        'pricing_note': 'Pricing depends on modules, users, and integrations.',
        'tagline': 'Turn manual operations into streamlined digital workflows.',
    },
    {
        'slug': 'ui-ux-design',
        'title': 'UI/UX Design',
        'summary': 'Clean user journeys and modern interfaces for better engagement.',
        'overview': 'We design product flows, wireframes, and polished interfaces that reduce friction and improve user satisfaction.',
        'ideal_for': 'Product teams, founders, and businesses redesigning existing apps.',
        'timeline': '4 to 12 working days depending on screens.',
        'icon_sprite': 'ui-ux-design',
        'feature_cards': [
            {'title': 'Wireframes', 'description': 'Flow-based planning before visual execution.', 'icon_sprite': 'process-flow'},
            {'title': 'Design System', 'description': 'Reusable components and style consistency.', 'icon_sprite': 'ui-ux-design'},
            {'title': 'Prototype', 'description': 'Clickable handoff-ready screen prototypes.', 'icon_sprite': 'landing-page'},
        ],
        'included_points': [
            {'title': 'Screen Set', 'text': 'Core screens with desktop and mobile behavior guidance.'},
            {'title': 'Interaction Notes', 'text': 'Developer-friendly notes for transitions and states.'},
            {'title': 'Asset Export', 'text': 'Icons and design assets for implementation.'},
        ],
        'pricing_note': 'Pricing depends on number of screens and complexity.',
        'tagline': 'Design experiences users understand instantly.',
    },
    {
        'slug': 'domains-hosting',
        'title': 'Domains and Hosting',
        'summary': 'Domain registration, hosting setup, SSL, and deployment support.',
        'overview': 'We help you buy the right domain and deploy your website with secure hosting and DNS management.',
        'ideal_for': 'Businesses launching a new online presence.',
        'timeline': '1 to 3 working days.',
        'icon_sprite': 'domains-hosting',
        'feature_cards': [
            {'title': 'Domain Setup', 'description': 'Domain purchase and DNS mapping.', 'icon_sprite': 'domains-hosting'},
            {'title': 'Hosting Setup', 'description': 'Server and SSL configuration.', 'icon_sprite': 'website-development'},
            {'title': 'Email Setup', 'description': 'Business email onboarding support.', 'icon_sprite': 'content-writing'},
        ],
        'included_points': [
            {'title': 'DNS Records', 'text': 'A, CNAME, and mail records configuration.'},
            {'title': 'SSL Security', 'text': 'HTTPS setup for secure traffic.'},
            {'title': 'Go-Live Support', 'text': 'Final checks and launch assistance.'},
        ],
        'pricing_note': 'Pricing depends on provider plan and period.',
        'tagline': 'Get online fast with reliable hosting foundations.',
    },
    {
        'slug': 'website-maintenance',
        'title': 'Website Maintenance',
        'summary': 'Ongoing website updates, backups, and uptime monitoring.',
        'overview': 'Keep your website secure and updated with regular maintenance and performance checks.',
        'ideal_for': 'Existing websites that need reliable support.',
        'timeline': 'Monthly support plans.',
        'icon_sprite': 'website-maintenance',
        'feature_cards': [
            {'title': 'Content Updates', 'description': 'Update banners, text, and sections quickly.', 'icon_sprite': 'content-writing'},
            {'title': 'Bug Fixes', 'description': 'Resolve layout and functionality issues.', 'icon_sprite': 'website-maintenance'},
            {'title': 'Health Checks', 'description': 'Regular backups and uptime checks.', 'icon_sprite': 'process-flow'},
        ],
        'included_points': [
            {'title': 'Backup Routine', 'text': 'Scheduled backups with restore support.'},
            {'title': 'Security Patch', 'text': 'Critical updates applied safely.'},
            {'title': 'Support Window', 'text': 'Prompt issue handling as per plan.'},
        ],
        'pricing_note': 'Pricing depends on update volume and SLA.',
        'tagline': 'Keep your website stable, secure, and up to date.',
    },
    {
        'slug': 'graphic-brand-design',
        'title': 'Graphic Design',
        'summary': 'Brand creatives, social media posts, and marketing visuals.',
        'overview': 'We design visual assets that communicate your brand clearly across web and social channels.',
        'ideal_for': 'Brands needing consistent visual communication.',
        'timeline': '2 to 7 working days depending on deliverables.',
        'icon_sprite': 'graphic-brand-design',
        'feature_cards': [
            {'title': 'Brand Creatives', 'description': 'Banners, posters, and campaign artwork.', 'icon_sprite': 'graphic-brand-design'},
            {'title': 'Social Media Kits', 'description': 'Editable post templates and stories.', 'icon_sprite': 'digital-marketing'},
            {'title': 'Web Assets', 'description': 'Optimized graphics for websites and apps.', 'icon_sprite': 'ui-ux-design'},
        ],
        'included_points': [
            {'title': 'Design Variants', 'text': 'Multiple options for selection.'},
            {'title': 'Source Files', 'text': 'Editable files with exports.'},
            {'title': 'Usage Guidance', 'text': 'Recommendations for digital publishing.'},
        ],
        'pricing_note': 'Pricing depends on asset count and complexity.',
        'tagline': 'Strong visuals that improve brand recall.',
    },
    {
        'slug': 'e-commerce-website',
        'title': 'E-commerce Websites',
        'summary': 'Online store setup with product catalog and checkout flow.',
        'overview': 'Launch your online store with product management, payment integration, and order tracking workflows.',
        'ideal_for': 'Retailers and product-based businesses.',
        'timeline': '1 to 4 weeks depending on catalog size.',
        'icon_sprite': 'e-commerce-website',
        'feature_cards': [
            {'title': 'Product Catalog', 'description': 'Manage products, categories, and pricing.', 'icon_sprite': 'e-commerce-website'},
            {'title': 'Checkout Flow', 'description': 'Smooth purchase journey design.', 'icon_sprite': 'web-application-development'},
            {'title': 'Order Tracking', 'description': 'Track and manage customer orders.', 'icon_sprite': 'process-flow'},
        ],
        'included_points': [
            {'title': 'Store Setup', 'text': 'Category and product onboarding support.'},
            {'title': 'Payment Setup', 'text': 'Payment gateway integration guidance.'},
            {'title': 'Admin Panel', 'text': 'Order and inventory handling workflow.'},
        ],
        'pricing_note': 'Pricing depends on features and integrations.',
        'tagline': 'Sell online with confidence and scalability.',
    },
    {
        'slug': 'social-network-website',
        'title': 'Social Network Sites',
        'summary': 'Community-style platforms for users, groups, and content sharing.',
        'overview': 'Build social interaction platforms with profiles, feeds, and engagement modules.',
        'ideal_for': 'Communities, creator networks, and niche groups.',
        'timeline': '3 to 8 weeks based on feature depth.',
        'icon_sprite': 'social-network-website',
        'feature_cards': [
            {'title': 'User Profiles', 'description': 'Profile creation and personalization.', 'icon_sprite': 'personal-website'},
            {'title': 'Feeds & Posts', 'description': 'Content posting and updates.', 'icon_sprite': 'social-network-website'},
            {'title': 'Moderation', 'description': 'Basic moderation and reporting tools.', 'icon_sprite': 'process-flow'},
        ],
        'included_points': [
            {'title': 'Authentication', 'text': 'Secure account sign-up and login.'},
            {'title': 'Engagement Tools', 'text': 'Comments, likes, and interaction workflows.'},
            {'title': 'Scalable Structure', 'text': 'Architecture suitable for growth.'},
        ],
        'pricing_note': 'Pricing depends on scale and modules.',
        'tagline': 'Build digital communities that stay engaged.',
    },
    {
        'slug': 'cms-website',
        'title': 'CMS Websites',
        'summary': 'Content-managed websites where your team can update pages easily.',
        'overview': 'We provide CMS-driven websites with admin-friendly editing and structured content management.',
        'ideal_for': 'Teams that update content frequently.',
        'timeline': '1 to 3 weeks based on page and role setup.',
        'icon_sprite': 'cms-website',
        'feature_cards': [
            {'title': 'Admin Panels', 'description': 'Manage pages, banners, and sections easily.', 'icon_sprite': 'cms-website'},
            {'title': 'Role Access', 'description': 'Permission control for editors and admins.', 'icon_sprite': 'process-flow'},
            {'title': 'Content Blocks', 'description': 'Reusable components for quick publishing.', 'icon_sprite': 'content-writing'},
        ],
        'included_points': [
            {'title': 'Editor Training', 'text': 'Basic team training for content updates.'},
            {'title': 'SEO Fields', 'text': 'Meta title and description support.'},
            {'title': 'Version Safety', 'text': 'Safer content update workflow.'},
        ],
        'pricing_note': 'Pricing depends on role setup and content modules.',
        'tagline': 'Control your website content without developer dependency.',
    },
    {
        'slug': 'content-writing',
        'title': 'Content Writing',
        'summary': 'Website content, SEO-friendly pages, and service copywriting.',
        'overview': 'Get clear, keyword-aware, and conversion-focused content tailored to your audience.',
        'ideal_for': 'Businesses launching or refreshing web content.',
        'timeline': '2 to 10 working days depending on page count.',
        'icon_sprite': 'content-writing',
        'feature_cards': [
            {'title': 'Website Copy', 'description': 'Service and landing page writing.', 'icon_sprite': 'landing-page'},
            {'title': 'SEO Drafting', 'description': 'Keyword-aware content structuring.', 'icon_sprite': 'content-seo-support'},
            {'title': 'Brand Voice', 'description': 'Tone aligned with your audience.', 'icon_sprite': 'graphic-brand-design'},
        ],
        'included_points': [
            {'title': 'Page Drafts', 'text': 'Structured drafts for quick publishing.'},
            {'title': 'Revision Round', 'text': 'One revision cycle based on feedback.'},
            {'title': 'Publishing Ready', 'text': 'Final content formatted for website upload.'},
        ],
        'pricing_note': 'Pricing depends on words and research depth.',
        'tagline': 'Say the right thing clearly and convert better.',
    },
]


def _service_by_slug(slug):
    for service in SOLUTION_SERVICES:
        if service['slug'] == slug:
            return service
    return None


def solutions_home(request):
    return render(request, 'solutions/home.html', {'solution_services': SOLUTION_SERVICES})


def service_detail(request, slug):
    service = _service_by_slug(slug)
    if not service:
        return redirect('solutions:home')
    return render(request, 'solutions/service_detail.html', {'service': service})


@login_required
def book_solution(request):
    selected_service = request.GET.get('service', '').strip()
    initial_data = {'service_name': selected_service}

    if request.method == 'POST':
        form = SolutionBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.address_line = 'N/A'
            booking.city = 'N/A'
            booking.pincode = '000000'
            booking.save()
            return redirect(f"{redirect('solutions:booking_success').url}?booking={booking.id}")
    else:
        form = SolutionBookingForm(initial=initial_data)

    return render(request, 'solutions/book.html', {'form': form})


@login_required
def booking_success(request):
    booking_id = request.GET.get('booking')
    booking = None
    if booking_id:
        booking = SolutionBooking.objects.filter(id=booking_id, user=request.user).first()
    return render(request, 'solutions/booking_success.html', {'booking': booking})


@login_required
def my_bookings(request):
    bookings = SolutionBooking.objects.filter(user=request.user)
    return render(request, 'solutions/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    if request.method != 'POST':
        return redirect('solutions:my_bookings')

    booking = get_object_or_404(SolutionBooking, id=booking_id, user=request.user)
    if booking.status in {SolutionBooking.STATUS_CANCELLED, SolutionBooking.STATUS_COMPLETED}:
        messages.info(request, 'This booking cannot be cancelled.')
        return redirect('solutions:my_bookings')

    booking.status = SolutionBooking.STATUS_CANCELLED
    booking.save(update_fields=['status'])
    messages.success(request, 'Your solution booking has been cancelled successfully.')
    return redirect('solutions:my_bookings')


@login_required
def reschedule_booking(request, booking_id):
    booking = get_object_or_404(SolutionBooking, id=booking_id, user=request.user)

    if booking.status in {SolutionBooking.STATUS_CANCELLED, SolutionBooking.STATUS_COMPLETED}:
        messages.error(request, 'This booking cannot be rescheduled.')
        return redirect('solutions:my_bookings')

    if request.method == 'POST':
        form = SolutionRescheduleForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solution booking updated successfully.')
            return redirect('solutions:my_bookings')
    else:
        form = SolutionRescheduleForm(instance=booking)

    return render(request, 'solutions/reschedule.html', {'form': form, 'booking': booking})
