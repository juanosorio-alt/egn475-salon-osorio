# Bella Vista Salon Booking Prototype

## Project Choice

Option B: Bella Vista Salon in Coral Gables.

I chose this project because I am more interested in organizing appointments
and improving customer service through clearly scheduled time slots than in
managing food orders. This project will let me focus on helping clients book
services and helping staff keep an organized appointment calendar.

## Problem Statement

For this project, we assume that Bella Vista Salon currently manages bookings
through scattered WhatsApp conversations. This makes it difficult for staff
to organize the appointment calendar efficiently and for clients to clearly
check their appointment status. Our prototype will allow clients to request
appointments by selecting a service, date, and time, while enabling staff to
confirm, complete, or cancel appointments through a structured interface.
This will centralize booking management and help reduce confusion caused
by scattered messages.

## Target Users

### Sofia Martinez — Client

- Role: Salon client with a busy work schedule.
- Goals: View services, prices, and durations; request an appointment that
  fits her schedule; and check her appointment status.
- Frustrations: Waiting for WhatsApp replies and searching message threads
  for appointment details.
- Technology comfort: Comfortable with smartphone apps and simple online forms.
- Quote: "I want to book an appointment around my work schedule and clearly
  see when it is confirmed."

### Daniel Perez — Receptionist

- Role: Salon receptionist responsible for managing appointments.
- Goals: Review requests, check stylist availability, organize the calendar,
  and confirm, complete, or cancel appointments.
- Frustrations: Switching between WhatsApp conversations and keeping track
  of booking details and changes.
- Technology comfort: Comfortable with messaging apps and basic computer
  tools; prefers a simple calendar with clear labels and statuses.
- Quote: "I need to see all appointments in one place so I can confirm
  bookings without mixing up times."

## Must Have Features

1. Service catalog with descriptions, prices, and estimated durations for
   haircuts, hairstyling, and hair coloring.
2. Appointment request form collecting client name, phone, email, service,
   date, and time, with acknowledgment of the cancellation policy.
3. Availability rules that account for service duration and existing bookings.
   Appointments must fit within Tuesday–Saturday, 9 a.m.–6 p.m., and be
   requested between 24 hours and 30 days ahead.
4. My Appointments page showing appointment details and current status.
5. Staff calendar showing pending requests and scheduled appointments,
   allowing staff to check availability and assign a stylist.
6. Appointment status management for the receptionist and manager:
   pending requests can be confirmed or canceled, and confirmed appointments
   can be completed or canceled.
7. Services administration allowing the manager to add or update service
   descriptions, prices, and durations.

## Not in This Prototype

- Online payments, deposits, or cancellation fees.
- Automated SMS or email notifications and reminders.
- A native iOS or Android mobile app.
- Loyalty points, memberships, or rewards.
- Client selection of a specific stylist.
- A Spanish-language interface in the initial version.

## Current Implementation

The Assignment 1.1 application currently provides two Flask routes:
- `/`: Displays the welcome message.
- `/about`: Displays the salon description.

The booking features above define the planned prototype scope.

## Run the Current Application on macOS

With Python 3.12 installed, run these commands from the project folder:

    python3.12 -m venv .venv
    source .venv/bin/activate
    python -m pip install flask
    python -m flask --app app run --debug

If the virtual environment already exists and Flask is installed,
only activate it and run the final command.