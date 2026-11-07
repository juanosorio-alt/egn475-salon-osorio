# User stories

1. **[MUST]** As a salon receptionist, I want to see appointments for a selected date, so that I can plan the salon’s schedule.
  - Given the selected date has a pending request and a confirmed appointment, when I open that date in the staff calendar, then I see the service, time, and status for both entries.
  - Given the selected date has no requests or appointments, when I open that date in the staff calendar, then I see the message “No appointments for this date.”.

2. **[MUST]** As a salon receptionist, I want to confirm a pending appointment request, so that the client knows the visit is scheduled.
    - Given a Pending 60-minute appointment starts at 2:00 p.m. and the selected stylist is free from 2:00 to 3:00 p.m., when I confirm the request, then the app saves the stylist assignment and changes the status to Confirmed.
    - Given a Pending 60-minute appointment starts at 2:00 p.m. and the selected stylist already has a Confirmed appointment from 2:30 to 3:00 p.m., when I try to confirm the request, then the app shows a scheduling conflict and keeps the request Pending.

3. **[MUST]** As a salon receptionist, I want to mark a finished appointment as completed, so that I can see which clients have already been served.
   - Given an appointment is Confirmed, when I select Mark Completed after the service, then the appointment status changes to Completed.
   - Given an appointment is Pending, when I open its details, then the Mark Completed option is unavailable and the status remains Pending.

4. **[MUST]** As a salon receptionist, I want to cancel an appointment when a client calls it off, so that the staff calendar shows that the visit will not take place.
  - Given an appointment is Confirmed or Pending, when I select Cancel Appointment, then the status changes to Canceled and the staff calendar displays it as Canceled.
  - Given an appointment is already Completed, when I open its details, then Cancel Appointment is unavailable and the status remains Completed.

5. **[MUST]** As a salon client, I want to see each service’s description, price, and estimated duration, so that I can choose a service that fits my budget and schedule.
  - Given a haircut is listed with a description, a price of $35, and a duration of 30 minutes, when I open the Services page, then I see the haircut description, the $35 price, and the 30-minute duration.
  - Given the catalog has no services, when I open the Services page, then I see the message “No services are currently available.”.

6. **[MUST]** As a salon client, I want to see available times for my selected service, so that I can choose a time that fits my schedule.
   - Given I select a 60-minute service on an open day within the booking window of 24 hours to 30 days in advance and a stylist is free from 4:00 to 5:00 p.m., when I view available times for that date, then 4:00 p.m. is offered.
   - Given I select a 60-minute service on an open day within the booking window and the salon closes at 6:00 p.m., when I view available times for that date, then 5:30 p.m. is not offered because the service would end at 6:30 p.m.

7. **[MUST]** As a salon client, I want to submit an appointment request for my chosen service and time, so that the salon can review my request.
   - Given I have selected a service, date, and available time, entered my name, phone number, and email address, and acknowledged the cancellation policy, when I submit the form, then the app creates a request with the status Pending.
   - Given I have completed all other required fields and acknowledged the cancellation policy but left the email field blank, when I submit the form, then the app shows “Email is required” next to that field and creates no request.

8. **[MUST]** As a salon client, I want to see my appointment status, so that I know whether the salon has confirmed my visit.
   - Given I have one appointment in each status (Pending, Confirmed, Completed, and Canceled) and another client also has an appointment, when I open My Appointments, then I see only my four appointments, each with its correct status.
   - Given I have no appointments but other clients have bookings, when I open My Appointments, then I see the message “You have no appointments.”