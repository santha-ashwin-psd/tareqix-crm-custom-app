
# import frappe
# import json
# from email.utils import parseaddr
# from openai import OpenAI


# # ============================================================
# # EXISTING FUNCTION
# # Communication already linked to Lead
# # ============================================================

# @frappe.whitelist()
# def extract_lead_from_communication(communication_name):
#     logs = []

#     logs.append("========== AI LEAD EXTRACTION START ==========")
#     logs.append("Communication: " + str(communication_name))

#     try:

#         # ---------------------------------------------------------
#         # 1. Get Communication
#         # ---------------------------------------------------------

#         communication = frappe.get_doc(
#             "Communication",
#             communication_name
#         )

#         logs.append(
#             "Reference Doctype: "
#             + str(communication.reference_doctype)
#         )

#         logs.append(
#             "Reference Name: "
#             + str(communication.reference_name)
#         )

#         logs.append(
#             "Subject: "
#             + str(communication.subject)
#         )

#         if communication.reference_doctype != "Lead":

#             logs.append(
#                 "Skipped: Communication is not linked to Lead"
#             )

#             frappe.log_error(
#                 "\n".join(logs),
#                 "AI Lead Extraction - Skipped"
#             )

#             return {
#                 "success": False,
#                 "message": "Communication is not linked to Lead"
#             }

#         if not communication.reference_name:

#             logs.append(
#                 "Skipped: No Lead reference found"
#             )

#             frappe.log_error(
#                 "\n".join(logs),
#                 "AI Lead Extraction - Skipped"
#             )

#             return {
#                 "success": False,
#                 "message": "No Lead reference found"
#             }

#         # ---------------------------------------------------------
#         # 2. Get email text
#         # ---------------------------------------------------------

#         email_text = (
#             communication.text_content
#             or communication.content
#             or ""
#         )

#         if not email_text.strip():

#             logs.append(
#                 "Skipped: Email content is empty"
#             )

#             frappe.log_error(
#                 "\n".join(logs),
#                 "AI Lead Extraction - Skipped"
#             )

#             return {
#                 "success": False,
#                 "message": "Email content is empty"
#             }

#         logs.append("Email content found: YES")
#         logs.append(
#             "Email content length: "
#             + str(len(email_text))
#         )

#         # ---------------------------------------------------------
#         # 3. Get OpenAI API key
#         # ---------------------------------------------------------

#         api_key = frappe.conf.get("openai_api_key")

#         if not api_key:

#             logs.append(
#                 "OpenAI API key found: NO"
#             )

#             logs.append(
#                 "ERROR: openai_api_key is missing from site config"
#             )

#             frappe.log_error(
#                 "\n".join(logs),
#                 "AI Lead Extraction - Error"
#             )

#             return {
#                 "success": False,
#                 "message": "OpenAI API key is not configured"
#             }

#         logs.append(
#             "OpenAI API key found: YES"
#         )

#         # ---------------------------------------------------------
#         # 4. Create OpenAI client
#         # ---------------------------------------------------------

#         client = OpenAI(
#             api_key=api_key
#         )

#         logs.append(
#             "OpenAI client created: YES"
#         )

#         logs.append(
#             "OpenAI model: gpt-5.6-luna"
#         )

#         logs.append(
#             "Sending request to OpenAI..."
#         )

#         # ---------------------------------------------------------
#         # 5. AI extraction
#         # ---------------------------------------------------------

#         response = client.responses.create(

#             model="gpt-5.6-luna",

#             instructions="""
# Extract customer information from the email.

# Return ONLY valid JSON with exactly these keys:

# name
# company
# phone
# email
# requirement
# location

# Rules:

# - If information is missing, return null.
# - Do not invent information.
# - Do not infer information that is not explicitly present.
# - Extract only information explicitly available in the email.
# - Keep the customer's full name in the name field.
# - Keep company name in company.
# - Keep phone number exactly as provided where possible.
# - Keep email address exactly as provided.
# - Keep requirement as a concise description of what the customer is asking for.
# - Keep location only if explicitly mentioned.
# """,

#             input=email_text
#         )

#         logs.append(
#             "OpenAI request completed: YES"
#         )

#         # ---------------------------------------------------------
#         # 6. Get AI output
#         # ---------------------------------------------------------

#         output_text = response.output_text

#         logs.append(
#             "AI response received: YES"
#         )

#         logs.append(
#             "AI response length: "
#             + str(len(output_text))
#         )

#         logs.append(
#             "AI response:"
#         )

#         logs.append(
#             output_text
#         )

#         if not output_text:

#             logs.append(
#                 "ERROR: AI returned empty response"
#             )

#             frappe.log_error(
#                 "\n".join(logs),
#                 "AI Lead Extraction - Error"
#             )

#             return {
#                 "success": False,
#                 "message": "AI returned empty response"
#             }

#         # ---------------------------------------------------------
#         # 7. Parse JSON
#         # ---------------------------------------------------------

#         try:

#             extracted = json.loads(
#                 output_text
#             )

#         except Exception:

#             logs.append(
#                 "ERROR: AI response is not valid JSON"
#             )

#             frappe.log_error(
#                 "\n".join(logs),
#                 "AI Lead Extraction - Error"
#             )

#             return {
#                 "success": False,
#                 "message": "AI response was not valid JSON",
#                 "raw_response": output_text
#             }

#         logs.append(
#             "JSON parsed successfully: YES"
#         )

#         # ---------------------------------------------------------
#         # 8. Log extracted values
#         # ---------------------------------------------------------

#         logs.append(
#             "========== EXTRACTED DATA =========="
#         )

#         logs.append(
#             "Name: "
#             + str(extracted.get("name"))
#         )

#         logs.append(
#             "Company: "
#             + str(extracted.get("company"))
#         )

#         logs.append(
#             "Phone: "
#             + str(extracted.get("phone"))
#         )

#         logs.append(
#             "Email: "
#             + str(extracted.get("email"))
#         )

#         logs.append(
#             "Requirement: "
#             + str(extracted.get("requirement"))
#         )

#         logs.append(
#             "Location: "
#             + str(extracted.get("location"))
#         )

#         # ---------------------------------------------------------
#         # 9. Get Lead
#         # ---------------------------------------------------------

#         lead = frappe.get_doc(
#             "Lead",
#             communication.reference_name
#         )

#         logs.append(
#             "Lead loaded: "
#             + str(lead.name)
#         )

#         # ---------------------------------------------------------
#         # 10. Update First Name / Last Name
#         # ---------------------------------------------------------

#         if extracted.get("name"):

#             full_name = str(
#                 extracted.get("name")
#             ).strip()

#             parts = full_name.split(
#                 " ",
#                 1
#             )

#             lead.first_name = parts[0]

#             if len(parts) > 1:

#                 lead.last_name = parts[1]

#             logs.append(
#                 "Lead name updated: "
#                 + full_name
#             )

#         # ---------------------------------------------------------
#         # 11. Update Company
#         # ---------------------------------------------------------

#         if extracted.get("company"):

#             lead.company_name = (
#                 extracted.get("company")
#             )

#             logs.append(
#                 "Lead company updated: "
#                 + str(
#                     extracted.get("company")
#                 )
#             )

#         # ---------------------------------------------------------
#         # 12. Update Phone
#         # ---------------------------------------------------------

#         if extracted.get("phone"):

#             lead.phone = (
#                 extracted.get("phone")
#             )

#             logs.append(
#                 "Lead phone updated: "
#                 + str(
#                     extracted.get("phone")
#                 )
#             )

#         # ---------------------------------------------------------
#         # 13. Update Email
#         # ---------------------------------------------------------

#         if extracted.get("email"):

#             lead.email_id = (
#                 extracted.get("email")
#             )

#             logs.append(
#                 "Lead email updated: "
#                 + str(
#                     extracted.get("email")
#                 )
#             )

#         # ---------------------------------------------------------
#         # Requirement and Location
#         # ---------------------------------------------------------

#         logs.append(
#             "Requirement received: "
#             + str(
#                 extracted.get("requirement")
#             )
#         )

#         logs.append(
#             "Location received: "
#             + str(
#                 extracted.get("location")
#             )
#         )

#         # ---------------------------------------------------------
#         # 14. Save Lead
#         # ---------------------------------------------------------

#         lead.save(
#             ignore_permissions=True
#         )

#         logs.append(
#             "Lead saved successfully: YES"
#         )

#         logs.append(
#             "Lead updated: "
#             + str(lead.name)
#         )

#         logs.append(
#             "========== AI LEAD EXTRACTION SUCCESS =========="
#         )

#         frappe.log_error(
#             "\n".join(logs),
#             "AI Lead Extraction - Success"
#         )

#         return {
#             "success": True,
#             "lead": lead.name,
#             "data": extracted
#         }

#     except Exception as e:

#         logs.append(
#             "========== AI LEAD EXTRACTION FAILED =========="
#         )

#         logs.append(
#             "ERROR: "
#             + str(e)
#         )

#         logs.append(
#             "TRACEBACK:"
#         )

#         logs.append(
#             frappe.get_traceback()
#         )

#         frappe.log_error(
#             "\n".join(logs),
#             "AI Lead Extraction - Error"
#         )

#         return {
#             "success": False,
#             "message": str(e)
#         }


# # ============================================================
# # NEW FUNCTION
# #
# # Communication -> AI -> CREATE NEW LEAD
# # ============================================================

# def create_lead_from_communication(communication_name):

#     logs = []

#     try:

#         logs.append(
#             "========== CREATE LEAD FROM COMMUNICATION START =========="
#         )

#         logs.append(
#             "Communication: "
#             + str(communication_name)
#         )

#         # ---------------------------------------------------------
#         # 1. Get Communication
#         # ---------------------------------------------------------

#         communication = frappe.get_doc(
#             "Communication",
#             communication_name
#         )

#         logs.append(
#             "Subject: "
#             + str(communication.subject)
#         )

#         logs.append(
#             "Sender: "
#             + str(communication.sender)
#         )

#         # ---------------------------------------------------------
#         # 2. Make sure this is a received email
#         # ---------------------------------------------------------

#         if communication.sent_or_received != "Received":

#             logs.append(
#                 "Skipped: Communication is not a received email"
#             )

#             return {
#                 "success": False,
#                 "message": "Communication is not a received email"
#             }

#         # ---------------------------------------------------------
#         # 3. Prevent duplicate processing
#         # ---------------------------------------------------------

#         if (
#             communication.reference_doctype == "Lead"
#             and communication.reference_name
#         ):

#             logs.append(
#                 "Communication already linked to Lead: "
#                 + str(communication.reference_name)
#             )

#             return {
#                 "success": True,
#                 "skipped": True,
#                 "lead": communication.reference_name
#             }

#         # ---------------------------------------------------------
#         # 4. Get email content
#         # ---------------------------------------------------------

#         email_text = (
#             communication.text_content
#             or communication.content
#             or ""
#         )

#         if not email_text.strip():

#             logs.append(
#                 "ERROR: Communication email content is empty"
#             )

#             frappe.log_error(
#                 "\n".join(logs),
#                 "AI Lead Creation - Empty Email"
#             )

#             return {
#                 "success": False,
#                 "message": "Communication email content is empty"
#             }

#         logs.append(
#             "Email content found: YES"
#         )

#         logs.append(
#             "Email content length: "
#             + str(len(email_text))
#         )

#         # ---------------------------------------------------------
#         # 5. Get OpenAI API key
#         # ---------------------------------------------------------

#         api_key = frappe.conf.get(
#             "openai_api_key"
#         )

#         if not api_key:

#             logs.append(
#                 "ERROR: OpenAI API key not configured"
#             )

#             frappe.log_error(
#                 "\n".join(logs),
#                 "AI Lead Creation - Error"
#             )

#             raise Exception(
#                 "OpenAI API key is not configured"
#             )

#         # ---------------------------------------------------------
#         # 6. Create OpenAI client
#         # ---------------------------------------------------------

#         client = OpenAI(
#             api_key=api_key
#         )

#         logs.append(
#             "OpenAI client created: YES"
#         )

#         # ---------------------------------------------------------
#         # 7. Extract customer information
#         # ---------------------------------------------------------

#         response = client.responses.create(

#             model="gpt-5.6-luna",

#             instructions="""
# Extract customer information and classify the email based on the email subject and body.

# Return ONLY valid JSON with exactly these keys:

# name
# company
# phone
# email
# requirement
# location
# lead_type
# candidate_category
# urgency_level
# summary
# is_relevant

# Rules:

# GENERAL EXTRACTION:

# - If information is missing, return null.
# - Do not invent information.
# - Extract only information explicitly available in the email.
# - Keep the customer's full name in the name field.
# - Keep company name in company.
# - Keep phone number exactly as provided where possible.
# - Keep email address exactly as provided in the email body.
# - Do NOT use the sender's email address as the email field. The Python code will use the sender address as a fallback if no email address is present in the email body.
# - Keep requirement as a concise description of what the customer is asking for.
# - Keep location only if explicitly mentioned.

# LEAD TYPE:

# The allowed values for lead_type are ONLY:

# "Company Enquiry"
# "Candidate Application"
# "Other"

# Classify the email based on what the sender is asking for.

# Use "Candidate Application" when the sender is a candidate/person looking for a job, employment, vacancy, work opportunity, career opportunity, or asking to be considered for a job.

# Use "Company Enquiry" when the sender represents a company/employer/organization and is asking for workers, employees, candidates, manpower, staff, recruitment, hiring, or candidates for a job requirement.

# Use "Other" when:
# - The email clearly contains both a company requirement and a candidate job request.
# - The sender's purpose cannot be determined reliably.
# - The email is not clearly a company enquiry or candidate application.

# Do not determine lead_type only from the sender's email address or company name. Use the actual meaning of the email.

# CANDIDATE CATEGORY:

# The allowed values for candidate_category are ONLY:

# "Skilled"
# "Semi Skilled"
# "Un Skilled"
# "IT Professional"
# "Other"

# Determine the category from the job, worker, employee, candidate, skill, qualification, or profession mentioned in the email.

# Use "Skilled" when the requirement clearly needs skilled workers or a skilled trade/profession.

# Use "Semi Skilled" when the requirement clearly indicates semi-skilled workers.

# Use "Un Skilled" when the requirement clearly indicates unskilled/general workers/labour/helpers or similar work that does not require a specific skill.

# Use "IT Professional" when the requirement is clearly related to IT/software/technology professionals such as software developers, programmers, IT engineers, system administrators, network engineers, data professionals, cybersecurity professionals, etc.

# Use "Other" when the skill category cannot be determined reliably from the email.

# Do not guess the category when the email does not provide enough information.

# URGENCY LEVEL:

# The allowed values for urgency_level are ONLY:

# "Low Urgency"
# "Medium Urgency"
# "High Urgency"

# Determine urgency from the actual wording and context of the email.

# Use "High Urgency" when the email clearly indicates immediate or very urgent action, for example: urgent, urgently, immediate, immediately, ASAP, emergency, critical, right away, required today, immediate requirement, or equivalent wording.

# Use "Medium Urgency" when the email indicates a normal or reasonably soon requirement, for example: soon, shortly, priority, looking to fill, required in the near future, or similar wording.

# Use "Low Urgency" when the email clearly indicates a low-priority, future, planned, or non-urgent requirement.

# If the email does not mention or clearly indicate any urgency, ALWAYS use "Medium Urgency".

# SUMMARY:

# Create a concise plain-text summary of the email.
# - Summarize the main purpose of the email and the important requirement/request.
# - Include important quantities, job/skill requirements, services requested, company/candidate context, or other important details when present.
# - Keep the summary short and useful for viewing on the Lead record.
# - Do not include greetings, signatures, email addresses, or unnecessary formatting.
# - Do not invent information.
# - Return the summary as plain text, not JSON or Markdown.

# RELEVANCE:

# - Return is_relevant as true ONLY when the email is genuinely about:
#   1. A candidate/person seeking a job, employment, vacancy, work opportunity, or career opportunity.
#   2. A company/employer/organization seeking employees, workers, candidates, manpower, staff, recruitment, or hiring.
#   3. An email containing BOTH a company employee requirement AND a candidate job request.
# - If the email contains BOTH a company requirement and a candidate job request:
#   - is_relevant MUST be true.
#   - lead_type MUST be "Other".
# - Return is_relevant as false for normal conversations, replies, acknowledgements, meeting coordination, quotations/discussions without a recruitment requirement, newsletters, notifications, signatures, general messages, or any email that is not genuinely a candidate application or company employee/recruitment enquiry.
# - is_relevant MUST be a boolean: true or false.

# IMPORTANT:
# - lead_type MUST be exactly one of the three allowed values.
# - candidate_category MUST be exactly one of the five allowed values.
# - urgency_level MUST be exactly one of the three allowed values.
# - Do not return explanations for the classification.
# - Return ONLY valid JSON.
# """,

#             input=email_text
#         )

#         output_text = response.output_text

#         if not output_text:

#             raise Exception(
#                 "OpenAI returned an empty response"
#             )

#         logs.append(
#             "AI response:"
#         )

#         logs.append(
#             output_text
#         )

#         # ---------------------------------------------------------
#         # 8. Parse JSON
#         # ---------------------------------------------------------

#         try:

#             extracted = json.loads(
#                 output_text
#             )

#         except Exception:

#             logs.append(
#                 "ERROR: AI response is not valid JSON"
#             )

#             logs.append(
#                 "Raw response: "
#                 + str(output_text)
#             )

#             raise Exception(
#                 "AI response was not valid JSON"
#             )

#         # ---------------------------------------------------------
#         # 9. Log extracted information
#         # ---------------------------------------------------------

#         logs.append(
#             "========== EXTRACTED DATA =========="
#         )

#         logs.append(
#             "Name: "
#             + str(extracted.get("name"))
#         )

#         logs.append(
#             "Company: "
#             + str(extracted.get("company"))
#         )

#         logs.append(
#             "Phone: "
#             + str(extracted.get("phone"))
#         )

#         logs.append(
#             "Email: "
#             + str(extracted.get("email"))
#         )

#         logs.append(
#             "Requirement: "
#             + str(extracted.get("requirement"))
#         )

#         logs.append(
#             "Location: "
#             + str(extracted.get("location"))
#         )

#         logs.append(
#             "Lead Type: "
#             + str(extracted.get("lead_type"))
#         )

#         logs.append(
#             "Candidate Category: "
#             + str(extracted.get("candidate_category"))
#         )

#         logs.append(
#             "Urgency Level: "
#             + str(extracted.get("urgency_level"))
#         )

#         logs.append(
#             "Summary: "
#             + str(extracted.get("summary"))
#         )

#         logs.append(
#             "Relevant Email: "
#             + str(extracted.get("is_relevant"))
#         )

#         # ---------------------------------------------------------
#         # 10. CREATE NEW LEAD
#         # ---------------------------------------------------------

#         lead = frappe.new_doc(
#             "Lead"
#         )

#         # ---------------------------------------------------------
#         # Name
#         # ---------------------------------------------------------

#         if extracted.get("name"):

#             full_name = str(
#                 extracted.get("name")
#             ).strip()

#             parts = full_name.split(
#                 " ",
#                 1
#             )

#             lead.first_name = parts[0]

#             if len(parts) > 1:

#                 lead.last_name = parts[1]

#             lead.lead_name = full_name

#         else:

#             # Fallback if name is not available

#             fallback_name = (
#                 extracted.get("email")
#                 or communication.sender
#                 or "Email Lead"
#             )

#             lead.lead_name = fallback_name
#             lead.first_name = fallback_name

#         # ---------------------------------------------------------
#         # Company
#         # ---------------------------------------------------------

#         if extracted.get("company"):

#             lead.company_name = (
#                 extracted.get("company")
#             )

#         # ---------------------------------------------------------
#         # Phone
#         # ---------------------------------------------------------

#         if extracted.get("phone"):

#             lead.phone = (
#                 extracted.get("phone")
#             )

#         # ---------------------------------------------------------
#         # Email
#         # ---------------------------------------------------------

#         if extracted.get("email"):

#             lead.email_id = (
#                 extracted.get("email")
#             )

#         # ---------------------------------------------------------
#         # Email fallback from sender
#         # ---------------------------------------------------------

#         if not extracted.get("email"):

#             sender_email = parseaddr(communication.sender or "")[1]

#             if sender_email:
#                 extracted["email"] = sender_email
#                 lead.email_id = sender_email

#                 logs.append(
#                     "Email not found in email content. Sender email used: "
#                     + sender_email
#                 )

#         # ---------------------------------------------------------
#         # Lead Type
#         # ---------------------------------------------------------

#         lead_type = extracted.get("lead_type")

#         if lead_type in [
#             "Company Enquiry",
#             "Candidate Application",
#             "Other"
#         ]:
#             lead.custom_lead_type = lead_type
#         else:
#             lead.custom_lead_type = "Other"

#         # ---------------------------------------------------------
#         # Candidate Category
#         # ---------------------------------------------------------

#         candidate_category = extracted.get("candidate_category")

#         if candidate_category in [
#             "Skilled",
#             "Semi Skilled",
#             "Un Skilled",
#             "IT Professional",
#             "Other"
#         ]:
#             lead.custom_candidate_category = candidate_category
#         else:
#             lead.custom_candidate_category = "Other"

#         # ---------------------------------------------------------
#         # Urgency Level
#         # ---------------------------------------------------------

#         urgency_level = extracted.get("urgency_level")

#         if urgency_level in [
#             "Low Urgency",
#             "Medium Urgency",
#             "High Urgency"
#         ]:
#             lead.custom_urgency_level = urgency_level
#         else:
#             lead.custom_urgency_level = "Medium Urgency"

#         # ---------------------------------------------------------
#         # Email Summary
#         # ---------------------------------------------------------

#         if extracted.get("summary"):
#             lead.custom_summary = str(extracted.get("summary")).strip()

#         # ---------------------------------------------------------
#         # 11. Create Lead
#         # ---------------------------------------------------------

#         # Only create a Lead for relevant recruitment emails.
#         # A mixed email containing BOTH a company employee requirement
#         # and a candidate job request is still relevant and is classified
#         # as lead_type = "Other".
#         if extracted.get("is_relevant") is not True:
#             logs.append(
#                 "Skipped: Email is not a relevant recruitment enquiry"
#             )

#             frappe.log_error(
#                 "\n".join(logs),
#                 "AI Lead Creation - Irrelevant Email Skipped"
#             )

#             return {
#                 "success": True,
#                 "skipped": True,
#                 "reason": "Irrelevant email",
#                 "communication": communication.name,
#                 "data": extracted
#             }

#         lead.insert(
#             ignore_permissions=True
#         )
        
#         copy_communication_attachments_to_lead(
#             communication_name=communication.name,
#             lead_name=lead.name
#             )

#         logs.append(
#             "NEW LEAD CREATED: "
#             + str(lead.name)
#         )

#         # ---------------------------------------------------------
#         # 12. Link Communication to Lead
#         # ---------------------------------------------------------

#         frappe.db.set_value(
#             "Communication",
#             communication.name,
#             {
#                 "reference_doctype": "Lead",
#                 "reference_name": lead.name
#             },
#             update_modified=False
#         )

#         logs.append(
#             "Communication linked to Lead: "
#             + str(lead.name)
#         )

#         # ---------------------------------------------------------
#         # 13. Success
#         # ---------------------------------------------------------

#         logs.append(
#             "========== CREATE LEAD FROM COMMUNICATION SUCCESS =========="
#         )

#         frappe.log_error(
#             "\n".join(logs),
#             "AI Lead Creation - Success"
#         )

#         return {
#             "success": True,
#             "communication": communication.name,
#             "lead": lead.name,
#             "data": extracted
#         }

#     except Exception as e:

#         logs.append(
#             "========== CREATE LEAD FROM COMMUNICATION FAILED =========="
#         )

#         logs.append(
#             "ERROR: "
#             + str(e)
#         )

#         logs.append(
#             "TRACEBACK:"
#         )

#         logs.append(
#             frappe.get_traceback()
#         )

#         frappe.log_error(
#             "\n".join(logs),
#             "AI Lead Creation - Error"
#         )

#         # Important:
#         # Re-raise so the background job can fail cleanly.
#         raise


# # ============================================================
# # BACKGROUND PROCESS
# # ============================================================

# def process_communication_to_lead(communication_name):

#     try:

#         return create_lead_from_communication(
#             communication_name
#         )

#     except Exception:

#         frappe.log_error(
#             frappe.get_traceback(),
#             "AI Lead Creation - Background Error"
#         )

#         raise


# # ============================================================
# # OLD QUEUE FUNCTION
# #
# # Kept so existing calls do not break.
# # ============================================================

# @frappe.whitelist()
# def queue_lead_ai_extraction(communication_name):

#     try:

#         frappe.enqueue(

#             "erpnext_update.api.process_lead_ai_in_background",

#             communication_name=communication_name,

#             queue="short",

#             enqueue_after_commit=True
#         )

#         return {
#             "success": True,
#             "queued": True,
#             "communication": communication_name
#         }

#     except Exception:

#         frappe.log_error(
#             frappe.get_traceback(),
#             "AI Lead Extraction - Queue Error"
#         )

#         return {
#             "success": False,
#             "queued": False,
#             "communication": communication_name
#         }


# # ============================================================
# # OLD BACKGROUND FUNCTION
# #
# # Kept for compatibility with your existing setup.
# # ============================================================

# def process_lead_ai_in_background(
#     communication_name
# ):

#     try:

#         result = extract_lead_from_communication(
#             communication_name
#         )

#         if not result.get("success"):

#             frappe.log_error(

#                 "AI extraction failed for Communication: "
#                 + str(communication_name)
#                 + "\n\n"
#                 + str(result),

#                 "AI Lead Extraction - Background Failed"
#             )

#         return result

#     except Exception:

#         frappe.log_error(
#             frappe.get_traceback(),
#             "AI Lead Extraction - Background Exception"
#         )

#         raise


# # ============================================================
# # COMMUNICATION AFTER INSERT
# #
# # THIS IS THE IMPORTANT NEW PART
# # ============================================================

# def communication_after_insert(
#     doc,
#     method=None
# ):

#     try:

#         # ---------------------------------------------------------
#         # Only process incoming emails
#         # ---------------------------------------------------------

#         if doc.sent_or_received != "Received":
#             return

#         # ---------------------------------------------------------
#         # Optional Email Account filter
#         #
#         # Your Outlook Email Account is:
#         # Tareqix Mail
#         # ---------------------------------------------------------

#         target_email_account = "Tareqix Mail"

#         if (
#             doc.email_account
#             and doc.email_account != target_email_account
#         ):
#             return

#         # ---------------------------------------------------------
#         # If already linked to Lead, don't process again
#         # ---------------------------------------------------------

#         if (
#             doc.reference_doctype == "Lead"
#             and doc.reference_name
#         ):
#             return

#         # ---------------------------------------------------------
#         # Queue new Communication -> Lead process
#         #
#         # enqueue_after_commit means:
#         #
#         # Communication is committed first.
#         #
#         # THEN AI processing starts.
#         # ---------------------------------------------------------

#         frappe.enqueue(

#             "erpnext_update.api.process_communication_to_lead",

#             communication_name=doc.name,

#             queue="long",

#             enqueue_after_commit=True,

#             timeout=600
#         )

#     except Exception:

#         # IMPORTANT:
#         #
#         # Never allow AI queue failure to break
#         # the Outlook email-pull transaction.

#         frappe.log_error(
#             frappe.get_traceback(),
#             "AI Lead Creation - Queue Error"
#         )
        
        
        
        
# def copy_communication_attachments_to_lead(communication_name, lead_name):
#     attachments = frappe.get_all(
#         "File",
#         filters={
#             "attached_to_doctype": "Communication",
#             "attached_to_name": communication_name
#         },
#         fields=["name", "file_name", "file_url", "is_private"]
#     )

#     for attachment in attachments:
#         # Avoid duplicate attachment
#         existing = frappe.db.exists(
#             "File",
#             {
#                 "attached_to_doctype": "Lead",
#                 "attached_to_name": lead_name,
#                 "file_name": attachment.file_name
#             }
#         )

#         if existing:
#             continue

#         frappe.db.set_value(
#             "File",
#             attachment.name,
#             {
#                 "attached_to_doctype": "Lead",
#                 "attached_to_name": lead_name,
#                 "attached_to_field": None
#             }
#         )

#     frappe.db.commit()



































































































































































import frappe
import json
from email.utils import parseaddr
from openai import OpenAI


# ============================================================
# EXISTING FUNCTION
# Communication already linked to Lead
# ============================================================

@frappe.whitelist()
def extract_lead_from_communication(communication_name):
    logs = []

    logs.append("========== AI LEAD EXTRACTION START ==========")
    logs.append("Communication: " + str(communication_name))

    try:

        # ---------------------------------------------------------
        # 1. Get Communication
        # ---------------------------------------------------------

        communication = frappe.get_doc(
            "Communication",
            communication_name
        )

        logs.append(
            "Reference Doctype: "
            + str(communication.reference_doctype)
        )

        logs.append(
            "Reference Name: "
            + str(communication.reference_name)
        )

        logs.append(
            "Subject: "
            + str(communication.subject)
        )

        if communication.reference_doctype != "Lead":

            logs.append(
                "Skipped: Communication is not linked to Lead"
            )

            frappe.log_error(
                "\n".join(logs),
                "AI Lead Extraction - Skipped"
            )

            return {
                "success": False,
                "message": "Communication is not linked to Lead"
            }

        if not communication.reference_name:

            logs.append(
                "Skipped: No Lead reference found"
            )

            frappe.log_error(
                "\n".join(logs),
                "AI Lead Extraction - Skipped"
            )

            return {
                "success": False,
                "message": "No Lead reference found"
            }

        # ---------------------------------------------------------
        # 2. Get email text
        # ---------------------------------------------------------

        email_text = (
            communication.text_content
            or communication.content
            or ""
        )

        if not email_text.strip():

            logs.append(
                "Skipped: Email content is empty"
            )

            frappe.log_error(
                "\n".join(logs),
                "AI Lead Extraction - Skipped"
            )

            return {
                "success": False,
                "message": "Email content is empty"
            }

        logs.append("Email content found: YES")
        logs.append(
            "Email content length: "
            + str(len(email_text))
        )

        # ---------------------------------------------------------
        # 3. Get OpenAI API key
        # ---------------------------------------------------------

        api_key = frappe.conf.get("openai_api_key")

        if not api_key:

            logs.append(
                "OpenAI API key found: NO"
            )

            logs.append(
                "ERROR: openai_api_key is missing from site config"
            )

            frappe.log_error(
                "\n".join(logs),
                "AI Lead Extraction - Error"
            )

            return {
                "success": False,
                "message": "OpenAI API key is not configured"
            }

        logs.append(
            "OpenAI API key found: YES"
        )

        # ---------------------------------------------------------
        # 4. Create OpenAI client
        # ---------------------------------------------------------

        client = OpenAI(
            api_key=api_key
        )

        logs.append(
            "OpenAI client created: YES"
        )

        logs.append(
            "OpenAI model: gpt-5.6-luna"
        )

        logs.append(
            "Sending request to OpenAI..."
        )

        # ---------------------------------------------------------
        # 5. AI extraction
        # ---------------------------------------------------------

        response = client.responses.create(

           #model="gpt-5.6-luna",
           model="gpt-4",

            instructions="""
Extract customer information from the email.

Return ONLY valid JSON with exactly these keys:

name
company
phone
email
requirement
location

Rules:

- If information is missing, return null.
- Do not invent information.
- Do not infer information that is not explicitly present.
- Extract only information explicitly available in the email.
- Keep the customer's full name in the name field.
- Keep company name in company.
- Keep phone number exactly as provided where possible.
- Keep email address exactly as provided.
- Keep requirement as a concise description of what the customer is asking for.
- Keep location only if explicitly mentioned.
""",

            input=email_text
        )

        logs.append(
            "OpenAI request completed: YES"
        )

        # ---------------------------------------------------------
        # 6. Get AI output
        # ---------------------------------------------------------

        output_text = response.output_text

        logs.append(
            "AI response received: YES"
        )

        logs.append(
            "AI response length: "
            + str(len(output_text))
        )

        logs.append(
            "AI response:"
        )

        logs.append(
            output_text
        )

        if not output_text:

            logs.append(
                "ERROR: AI returned empty response"
            )

            frappe.log_error(
                "\n".join(logs),
                "AI Lead Extraction - Error"
            )

            return {
                "success": False,
                "message": "AI returned empty response"
            }

        # ---------------------------------------------------------
        # 7. Parse JSON
        # ---------------------------------------------------------

        try:

            extracted = json.loads(
                output_text
            )

        except Exception:

            logs.append(
                "ERROR: AI response is not valid JSON"
            )

            frappe.log_error(
                "\n".join(logs),
                "AI Lead Extraction - Error"
            )

            return {
                "success": False,
                "message": "AI response was not valid JSON",
                "raw_response": output_text
            }

        logs.append(
            "JSON parsed successfully: YES"
        )

        # ---------------------------------------------------------
        # 8. Log extracted values
        # ---------------------------------------------------------

        logs.append(
            "========== EXTRACTED DATA =========="
        )

        logs.append(
            "Name: "
            + str(extracted.get("name"))
        )

        logs.append(
            "Company: "
            + str(extracted.get("company"))
        )

        logs.append(
            "Phone: "
            + str(extracted.get("phone"))
        )

        logs.append(
            "Email: "
            + str(extracted.get("email"))
        )

        logs.append(
            "Requirement: "
            + str(extracted.get("requirement"))
        )

        logs.append(
            "Location: "
            + str(extracted.get("location"))
        )

        # ---------------------------------------------------------
        # 9. Get Lead
        # ---------------------------------------------------------

        lead = frappe.get_doc(
            "Lead",
            communication.reference_name
        )

        logs.append(
            "Lead loaded: "
            + str(lead.name)
        )

        # ---------------------------------------------------------
        # 10. Update First Name / Last Name
        # ---------------------------------------------------------

        if extracted.get("name"):

            full_name = str(
                extracted.get("name")
            ).strip()

            parts = full_name.split(
                " ",
                1
            )

            lead.first_name = parts[0]

            if len(parts) > 1:

                lead.last_name = parts[1]

            logs.append(
                "Lead name updated: "
                + full_name
            )

        # ---------------------------------------------------------
        # 11. Update Company
        # ---------------------------------------------------------

        if extracted.get("company"):

            lead.company_name = (
                extracted.get("company")
            )

            logs.append(
                "Lead company updated: "
                + str(
                    extracted.get("company")
                )
            )

        # ---------------------------------------------------------
        # 12. Update Phone
        # ---------------------------------------------------------

        if extracted.get("phone"):

            lead.phone = (
                extracted.get("phone")
            )

            logs.append(
                "Lead phone updated: "
                + str(
                    extracted.get("phone")
                )
            )

        # ---------------------------------------------------------
        # 13. Update Email
        # ---------------------------------------------------------

        if extracted.get("email"):

            lead.email_id = (
                extracted.get("email")
            )

            logs.append(
                "Lead email updated: "
                + str(
                    extracted.get("email")
                )
            )

        # ---------------------------------------------------------
        # Requirement and Location
        # ---------------------------------------------------------

        logs.append(
            "Requirement received: "
            + str(
                extracted.get("requirement")
            )
        )

        logs.append(
            "Location received: "
            + str(
                extracted.get("location")
            )
        )

        # ---------------------------------------------------------
        # 14. Save Lead
        # ---------------------------------------------------------

        lead.save(
            ignore_permissions=True
        )

        logs.append(
            "Lead saved successfully: YES"
        )

        logs.append(
            "Lead updated: "
            + str(lead.name)
        )

        logs.append(
            "========== AI LEAD EXTRACTION SUCCESS =========="
        )

        frappe.log_error(
            "\n".join(logs),
            "AI Lead Extraction - Success"
        )

        return {
            "success": True,
            "lead": lead.name,
            "data": extracted
        }

    except Exception as e:

        logs.append(
            "========== AI LEAD EXTRACTION FAILED =========="
        )

        logs.append(
            "ERROR: "
            + str(e)
        )

        logs.append(
            "TRACEBACK:"
        )

        logs.append(
            frappe.get_traceback()
        )

        frappe.log_error(
            "\n".join(logs),
            "AI Lead Extraction - Error"
        )

        return {
            "success": False,
            "message": str(e)
        }


# ============================================================
# NEW FUNCTION
#
# Communication -> AI -> CREATE NEW CRM LEAD
# ============================================================

def create_lead_from_communication(communication_name):

    logs = []

    try:

        logs.append(
            "========== CREATE CRM LEAD FROM COMMUNICATION START =========="
        )

        logs.append(
            "Communication: "
            + str(communication_name)
        )

        # ---------------------------------------------------------
        # 1. Get Communication
        # ---------------------------------------------------------

        communication = frappe.get_doc(
            "Communication",
            communication_name
        )

        logs.append(
            "Subject: "
            + str(communication.subject)
        )

        logs.append(
            "Sender: "
            + str(communication.sender)
        )

        # ---------------------------------------------------------
        # 2. Make sure this is a received email
        # ---------------------------------------------------------

        if communication.sent_or_received != "Received":

            logs.append(
                "Skipped: Communication is not a received email"
            )

            return {
                "success": False,
                "message": "Communication is not a received email"
            }

        # ---------------------------------------------------------
        # 3. Prevent duplicate processing
        # ---------------------------------------------------------

        if (
            communication.reference_doctype in [
                "Lead",
                "CRM Lead"
            ]
            and communication.reference_name
        ):

            logs.append(
                "Communication already linked to "
                + str(communication.reference_doctype)
                + ": "
                + str(communication.reference_name)
            )

            return {
                "success": True,
                "skipped": True,
                "lead": communication.reference_name
            }

        # ---------------------------------------------------------
        # 4. Get email content
        # ---------------------------------------------------------

        email_text = (
            communication.text_content
            or communication.content
            or ""
        )

        if not email_text.strip():

            logs.append(
                "ERROR: Communication email content is empty"
            )

            frappe.log_error(
                "\n".join(logs),
                "AI Lead Creation - Empty Email"
            )

            return {
                "success": False,
                "message": "Communication email content is empty"
            }

        logs.append(
            "Email content found: YES"
        )

        logs.append(
            "Email content length: "
            + str(len(email_text))
        )

        # ---------------------------------------------------------
        # 5. Get OpenAI API key
        # ---------------------------------------------------------

        api_key = frappe.conf.get(
            "openai_api_key"
        )

        if not api_key:

            logs.append(
                "ERROR: OpenAI API key not configured"
            )

            frappe.log_error(
                "\n".join(logs),
                "AI Lead Creation - Error"
            )

            raise Exception(
                "OpenAI API key is not configured"
            )

        # ---------------------------------------------------------
        # 6. Create OpenAI client
        # ---------------------------------------------------------

        client = OpenAI(
            api_key=api_key
        )

        logs.append(
            "OpenAI client created: YES"
        )

        # ---------------------------------------------------------
        # 7. Extract customer information
        # ---------------------------------------------------------

        response = client.responses.create(

            #model="gpt-5.6-luna",
            model="gpt-4",

            instructions="""
Extract customer information and classify the email based on the email subject and body.

Return ONLY valid JSON with exactly these keys:

name
company
phone
email
requirement
location
lead_type
candidate_category
urgency_level
summary
is_relevant

Rules:

GENERAL EXTRACTION:

- If information is missing, return null.
- Do not invent information.
- Extract only information explicitly available in the email.
- Keep the customer's full name in the name field.
- Keep company name in company.
- Keep phone number exactly as provided where possible.
- Keep email address exactly as provided in the email body.
- Do NOT use the sender's email address as the email field. The Python code will use the sender address as a fallback if no email address is present in the email body.
- Keep requirement as a concise description of what the customer is asking for.
- Keep location only if explicitly mentioned.

LEAD TYPE:

The allowed values for lead_type are ONLY:

"Company Enquiry"
"Candidate Application"
"Other"

Classify the email based on what the sender is asking for.

Use "Candidate Application" when the sender is a candidate/person looking for a job, employment, vacancy, work opportunity, career opportunity, or asking to be considered for a job.

Use "Company Enquiry" when the sender represents a company/employer/organization and is asking for workers, employees, candidates, manpower, staff, recruitment, hiring, or candidates for a job requirement.

Use "Other" when:
- The email clearly contains both a company requirement and a candidate job request.
- The sender's purpose cannot be determined reliably.
- The email is not clearly a company enquiry or candidate application.

Do not determine lead_type only from the sender's email address or company name. Use the actual meaning of the email.

CANDIDATE CATEGORY:

The allowed values for candidate_category are ONLY:

"Skilled"
"Semi Skilled"
"Un Skilled"
"IT Professional"
"Other"

Determine the category from the job, worker, employee, candidate, skill, qualification, or profession mentioned in the email.

Use "Skilled" when the requirement clearly needs skilled workers or a skilled trade/profession.

Use "Semi Skilled" when the requirement clearly indicates semi-skilled workers.

Use "Un Skilled" when the requirement clearly indicates unskilled/general workers/labour/helpers or similar work that does not require a specific skill.

Use "IT Professional" when the requirement is clearly related to IT/software/technology professionals such as software developers, programmers, IT engineers, system administrators, network engineers, data professionals, cybersecurity professionals, etc.

Use "Other" when the skill category cannot be determined reliably from the email.

Do not guess the category when the email does not provide enough information.

URGENCY LEVEL:

The allowed values for urgency_level are ONLY:

"Low Urgency"
"Medium Urgency"
"High Urgency"

Determine urgency from the actual wording and context of the email.

Use "High Urgency" when the email clearly indicates immediate or very urgent action, for example: urgent, urgently, immediate, immediately, ASAP, emergency, critical, right away, required today, immediate requirement, or equivalent wording.

Use "Medium Urgency" when the email indicates a normal or reasonably soon requirement, for example: soon, shortly, priority, looking to fill, required in the near future, or similar wording.

Use "Low Urgency" when the email clearly indicates a low-priority, future, planned, or non-urgent requirement.

If the email does not mention or clearly indicate any urgency, ALWAYS use "Medium Urgency".

SUMMARY:

Create a concise plain-text summary of the email.
- Summarize the main purpose of the email and the important requirement/request.
- Include important quantities, job/skill requirements, services requested, company/candidate context, or other important details when present.
- Keep the summary short and useful for viewing on the Lead record.
- Do not include greetings, signatures, email addresses, or unnecessary formatting.
- Do not invent information.
- Return the summary as plain text, not JSON or Markdown.

RELEVANCE:

- Return is_relevant as true ONLY when the email is genuinely about:
  1. A candidate/person seeking a job, employment, vacancy, work opportunity, or career opportunity.
  2. A company/employer/organization seeking employees, workers, candidates, manpower, staff, recruitment, or hiring.
  3. An email containing BOTH a company employee requirement AND a candidate job request.
- If the email contains BOTH a company requirement and a candidate job request:
  - is_relevant MUST be true.
  - lead_type MUST be "Other".
- Return is_relevant as false for normal conversations, replies, acknowledgements, meeting coordination, quotations/discussions without a recruitment requirement, newsletters, notifications, signatures, general messages, or any email that is not genuinely a candidate application or company employee/recruitment enquiry.
- is_relevant MUST be a boolean: true or false.

IMPORTANT:
- lead_type MUST be exactly one of the three allowed values.
- candidate_category MUST be exactly one of the five allowed values.
- urgency_level MUST be exactly one of the three allowed values.
- Do not return explanations for the classification.
- Return ONLY valid JSON.
""",

            input=email_text
        )

        output_text = response.output_text

        if not output_text:

            raise Exception(
                "OpenAI returned an empty response"
            )

        logs.append(
            "AI response:"
        )

        logs.append(
            output_text
        )

        # ---------------------------------------------------------
        # 8. Parse JSON
        # ---------------------------------------------------------

        try:

            extracted = json.loads(
                output_text
            )

        except Exception:

            logs.append(
                "ERROR: AI response is not valid JSON"
            )

            logs.append(
                "Raw response: "
                + str(output_text)
            )

            raise Exception(
                "AI response was not valid JSON"
            )

        # ---------------------------------------------------------
        # 9. Log extracted information
        # ---------------------------------------------------------

        logs.append(
            "========== EXTRACTED DATA =========="
        )

        logs.append(
            "Name: "
            + str(extracted.get("name"))
        )

        logs.append(
            "Company: "
            + str(extracted.get("company"))
        )

        logs.append(
            "Phone: "
            + str(extracted.get("phone"))
        )

        logs.append(
            "Email: "
            + str(extracted.get("email"))
        )

        logs.append(
            "Requirement: "
            + str(extracted.get("requirement"))
        )

        logs.append(
            "Location: "
            + str(extracted.get("location"))
        )

        logs.append(
            "Lead Type: "
            + str(extracted.get("lead_type"))
        )

        logs.append(
            "Candidate Category: "
            + str(extracted.get("candidate_category"))
        )

        logs.append(
            "Urgency Level: "
            + str(extracted.get("urgency_level"))
        )

        logs.append(
            "Summary: "
            + str(extracted.get("summary"))
        )

        logs.append(
            "Relevant Email: "
            + str(extracted.get("is_relevant"))
        )

        # ---------------------------------------------------------
        # 10. CREATE NEW CRM LEAD
        # ---------------------------------------------------------

        lead = frappe.new_doc(
            "CRM Lead"
        )

        # ---------------------------------------------------------
        # Name
        # ---------------------------------------------------------

        if extracted.get("name"):

            full_name = str(
                extracted.get("name")
            ).strip()

            parts = full_name.split(
                " ",
                1
            )

            lead.first_name = parts[0]

            if len(parts) > 1:

                lead.last_name = parts[1]

            lead.lead_name = full_name

        else:

            # Fallback if name is not available

            fallback_name = (
                extracted.get("email")
                or communication.sender
                or "Email Lead"
            )

            lead.lead_name = fallback_name
            lead.first_name = fallback_name

        # ---------------------------------------------------------
        # Company
        # CRM Lead uses "organization"
        # ---------------------------------------------------------

        if extracted.get("company"):

            lead.organization = (
                extracted.get("company")
            )

        # ---------------------------------------------------------
        # Phone
        # ---------------------------------------------------------

        if extracted.get("phone"):

            lead.mobile_no = (
                extracted.get("phone")
            )

        # ---------------------------------------------------------
        # Email
        # CRM Lead uses "email"
        # ---------------------------------------------------------

        if extracted.get("email"):

            lead.email = (
                extracted.get("email")
            )

        # ---------------------------------------------------------
        # Email fallback from sender
        # ---------------------------------------------------------

        if not extracted.get("email"):

            sender_email = parseaddr(communication.sender or "")[1]

            if sender_email:
                extracted["email"] = sender_email
                lead.email = sender_email

                logs.append(
                    "Email not found in email content. Sender email used: "
                    + sender_email
                )

        # ---------------------------------------------------------
        # Source
        # ---------------------------------------------------------

        lead.source = "Email"

        # ---------------------------------------------------------
        # Status
        # ---------------------------------------------------------

        lead.status = "New"

        # ---------------------------------------------------------
        # Lead Type
        # ---------------------------------------------------------

        lead_type = extracted.get("lead_type")

        if lead_type in [
            "Company Enquiry",
            "Candidate Application",
            "Other"
        ]:
            lead.custom_lead_type = lead_type
        else:
            lead.custom_lead_type = "Other"

        # ---------------------------------------------------------
        # Candidate Category
        # ---------------------------------------------------------

        candidate_category = extracted.get("candidate_category")

        if candidate_category in [
            "Skilled",
            "Semi Skilled",
            "Un Skilled",
            "IT Professional",
            "Other"
        ]:
            lead.custom_candidate_category = candidate_category
        else:
            lead.custom_candidate_category = "Other"

        # ---------------------------------------------------------
        # Urgency Level
        # ---------------------------------------------------------

        urgency_level = extracted.get("urgency_level")

        if urgency_level in [
            "Low Urgency",
            "Medium Urgency",
            "High Urgency"
        ]:
            lead.custom_urgency_level = urgency_level
        else:
            lead.custom_urgency_level = "Medium Urgency"

        # ---------------------------------------------------------
        # Email Summary
        # CRM Lead uses built-in Description field
        # ---------------------------------------------------------

        if extracted.get("summary"):
            lead.company_description = str(
                extracted.get("summary")
            ).strip()

        # ---------------------------------------------------------
        # 11. Create CRM Lead
        # ---------------------------------------------------------

        # Only create a CRM Lead for relevant recruitment emails.
        # A mixed email containing BOTH a company employee requirement
        # and a candidate job request is still relevant and is classified
        # as lead_type = "Other".
        if extracted.get("is_relevant") is not True:

            logs.append(
                "Skipped: Email is not a relevant recruitment enquiry"
            )

            frappe.log_error(
                "\n".join(logs),
                "AI Lead Creation - Irrelevant Email Skipped"
            )

            return {
                "success": True,
                "skipped": True,
                "reason": "Irrelevant email",
                "communication": communication.name,
                "data": extracted
            }

        lead.insert(
            ignore_permissions=True
        )

        copy_communication_attachments_to_lead(
            communication_name=communication.name,
            lead_name=lead.name
        )

        logs.append(
            "NEW CRM LEAD CREATED: "
            + str(lead.name)
        )

        # ---------------------------------------------------------
        # 12. Link Communication to CRM Lead
        # ---------------------------------------------------------

        frappe.db.set_value(
            "Communication",
            communication.name,
            {
                "reference_doctype": "CRM Lead",
                "reference_name": lead.name
            },
            update_modified=False
        )

        logs.append(
            "Communication linked to CRM Lead: "
            + str(lead.name)
        )

        # ---------------------------------------------------------
        # 13. Success
        # ---------------------------------------------------------

        logs.append(
            "========== CREATE CRM LEAD FROM COMMUNICATION SUCCESS =========="
        )

        frappe.log_error(
            "\n".join(logs),
            "AI Lead Creation - Success"
        )

        return {
            "success": True,
            "communication": communication.name,
            "lead": lead.name,
            "data": extracted
        }

    except Exception as e:

        logs.append(
            "========== CREATE CRM LEAD FROM COMMUNICATION FAILED =========="
        )

        logs.append(
            "ERROR: "
            + str(e)
        )

        logs.append(
            "TRACEBACK:"
        )

        logs.append(
            frappe.get_traceback()
        )

        frappe.log_error(
            "\n".join(logs),
            "AI Lead Creation - Error"
        )

        # Important:
        # Re-raise so the background job can fail cleanly.
        raise


# ============================================================
# BACKGROUND PROCESS
# ============================================================

def process_communication_to_lead(communication_name):

    try:

        return create_lead_from_communication(
            communication_name
        )

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "AI Lead Creation - Background Error"
        )

        raise


# ============================================================
# OLD QUEUE FUNCTION
#
# Kept so existing calls do not break.
# ============================================================

@frappe.whitelist()
def queue_lead_ai_extraction(communication_name):

    try:

        frappe.enqueue(

            "erpnext_update.api.process_lead_ai_in_background",

            communication_name=communication_name,

            queue="short",

            enqueue_after_commit=True
        )

        return {
            "success": True,
            "queued": True,
            "communication": communication_name
        }

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "AI Lead Extraction - Queue Error"
        )

        return {
            "success": False,
            "queued": False,
            "communication": communication_name
        }


# ============================================================
# OLD BACKGROUND FUNCTION
#
# Kept for compatibility with your existing setup.
# ============================================================

def process_lead_ai_in_background(
    communication_name
):

    try:

        result = extract_lead_from_communication(
            communication_name
        )

        if not result.get("success"):

            frappe.log_error(

                "AI extraction failed for Communication: "
                + str(communication_name)
                + "\n\n"
                + str(result),

                "AI Lead Extraction - Background Failed"
            )

        return result

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "AI Lead Extraction - Background Exception"
        )

        raise


# ============================================================
# COMMUNICATION AFTER INSERT
#
# THIS IS THE IMPORTANT NEW PART
# ============================================================

def communication_after_insert(
    doc,
    method=None
):

    try:

        # ---------------------------------------------------------
        # Only process incoming emails
        # ---------------------------------------------------------

        if doc.sent_or_received != "Received":
            return

        # ---------------------------------------------------------
        # Optional Email Account filter
        #
        # Your Outlook Email Account is:
        # Tareqix Mail
        # ---------------------------------------------------------

        target_email_account = "Tareqix Mail"

        if (
            doc.email_account
            and doc.email_account != target_email_account
        ):
            return

        # ---------------------------------------------------------
        # If already linked to Lead / CRM Lead, don't process again
        # ---------------------------------------------------------

        if (
            doc.reference_doctype in [
                "Lead",
                "CRM Lead"
            ]
            and doc.reference_name
        ):
            return

        # ---------------------------------------------------------
        # Queue new Communication -> CRM Lead process
        #
        # enqueue_after_commit means:
        #
        # Communication is committed first.
        #
        # THEN AI processing starts.
        # ---------------------------------------------------------

        frappe.enqueue(

            "erpnext_update.api.process_communication_to_lead",

            communication_name=doc.name,

            queue="long",

            enqueue_after_commit=True,

            timeout=600
        )

    except Exception:

        # IMPORTANT:
        #
        # Never allow AI queue failure to break
        # the Outlook email-pull transaction.

        frappe.log_error(
            frappe.get_traceback(),
            "AI Lead Creation - Queue Error"
        )


# ============================================================
# COPY COMMUNICATION ATTACHMENTS TO CRM LEAD
# ============================================================

def copy_communication_attachments_to_lead(
    communication_name,
    lead_name
):

    attachments = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Communication",
            "attached_to_name": communication_name
        },
        fields=[
            "name",
            "file_name",
            "file_url",
            "is_private"
        ]
    )

    for attachment in attachments:

        # Avoid duplicate attachment
        existing = frappe.db.exists(
            "File",
            {
                "attached_to_doctype": "CRM Lead",
                "attached_to_name": lead_name,
                "file_name": attachment.file_name
            }
        )

        if existing:
            continue

        frappe.db.set_value(
            "File",
            attachment.name,
            {
                "attached_to_doctype": "CRM Lead",
                "attached_to_name": lead_name,
                "attached_to_field": None
            }
        )

    frappe.db.commit()        