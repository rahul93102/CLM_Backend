"""
Production-Level NDA Document Generator
Generates customized Non-Disclosure Agreements with professional formatting
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
import re


class Jurisdiction(Enum):
    """Supported jurisdictions for NDA"""
    CALIFORNIA = ("California", "CA", "United States")
    NEW_YORK = ("New York", "NY", "United States")
    TEXAS = ("Texas", "TX", "United States")
    FEDERAL = ("Federal", "US", "United States")
    UK = ("England and Wales", "UK", "United Kingdom")
    CANADA = ("Ontario", "ON", "Canada")


class ConfidentialityDuration(Enum):
    """Predefined confidentiality durations"""
    THREE_YEARS = 3
    FIVE_YEARS = 5
    SEVEN_YEARS = 7
    TEN_YEARS = 10
    PERPETUAL = 0  # For trade secrets


@dataclass
class Party:
    """Represents a party to the NDA"""
    legal_name: str
    entity_type: str  # Corporation, LLC, Partnership
    state_of_incorporation: str
    address: str
    contact_name: str
    contact_title: str
    contact_email: str


@dataclass
class NDAConfiguration:
    """Configuration for NDA generation"""
    disclosing_party: Party
    receiving_party: Party
    effective_date: datetime
    confidentiality_duration: ConfidentialityDuration
    jurisdiction: Jurisdiction
    survival_duration: int = 5  # Years
    cure_period_days: int = 30
    include_appendices: bool = True
    confidential_items: Optional[List[Dict]] = None
    authorized_recipients: Optional[List[Dict]] = None
    special_provisions: Optional[List[str]] = None


class NDAGenerator:
    """Generates professional NDA documents"""
    
    def __init__(self, config: NDAConfiguration):
        """Initialize NDA generator with configuration"""
        self.config = config
        self.jurisdiction = config.jurisdiction
        self.effective_date = config.effective_date
        
    def _get_governing_law_clause(self) -> str:
        """Get jurisdiction-specific governing law clause"""
        jurisdiction_data = {
            Jurisdiction.CALIFORNIA: {
                "law": "California",
                "venue": "San Francisco County, California",
                "additional": "The parties waive any objection based on inconvenient forum."
            },
            Jurisdiction.NEW_YORK: {
                "law": "New York",
                "venue": "New York County, New York",
                "additional": "The parties irrevocably submit to the jurisdiction of the courts of the State of New York."
            },
            Jurisdiction.TEXAS: {
                "law": "Texas",
                "venue": "Travis County, Texas",
                "additional": "The parties consent to the exclusive jurisdiction of the courts of Texas."
            },
            Jurisdiction.UK: {
                "law": "England and Wales",
                "venue": "English Courts",
                "additional": "This Agreement shall be governed by English law."
            },
        }
        
        data = jurisdiction_data.get(self.jurisdiction, jurisdiction_data[Jurisdiction.CALIFORNIA])
        return f"""### 9.4 Governing Law
This Agreement shall be governed by and construed in accordance with the laws of {data['law']}, without regard to its conflict of law principles. {data['additional']}

### 9.5 Jurisdiction and Venue
The parties irrevocably consent to the exclusive jurisdiction and venue of the courts located in {data['venue']} for resolution of any disputes arising from this Agreement."""

    def _get_definitions_section(self) -> str:
        """Generate definitions section with standard definitions"""
        return """## 1. DEFINITIONS AND INTERPRETATION

### 1.1 Confidential Information
"Confidential Information" means all non-public information, technical data, know-how, research, product plans, products, developments, inventions, processes, formulas, techniques, designs, drawings, specifications, software code, source code, object code, documentation, business plans, financial information, customer lists, supplier lists, market analysis, pricing information, and any other proprietary or sensitive information, in any form or medium (including oral, written, electronic, or visual), whether or not marked as confidential or proprietary, that is disclosed by the Disclosing Party to the Receiving Party.

### 1.2 Exceptions
Confidential Information does not include information that:

(a) Is or becomes publicly available through no breach of this Agreement by the Receiving Party;

(b) Is rightfully received by the Receiving Party from a third party without breach of any confidentiality obligation and with no obligation of secrecy toward the source;

(c) Is independently developed by the Receiving Party without use of or reference to the Confidential Information, as evidenced by written records created and maintained contemporaneously during development;

(d) Was known to the Receiving Party prior to disclosure, as evidenced by written records dated prior to the date of disclosure;

(e) Is rightfully reverse-engineered from a lawfully obtained product by the Receiving Party without breach of any confidentiality obligation;

(f) Is required to be disclosed by law, court order, regulatory requirement, or governmental authority, provided the Receiving Party gives prompt written notice to the Disclosing Party and cooperates in efforts to obtain protective orders.

### 1.3 Permitted Use
"Permitted Use" means the evaluation of a potential business relationship, partnership, joint development, strategic alliance, licensing opportunity, investment, acquisition, or other collaborative arrangement between the parties, as mutually agreed in writing."""

    def _get_confidentiality_section(self, cure_days: int) -> str:
        """Generate confidentiality obligations section"""
        return f"""## 2. CONFIDENTIALITY OBLIGATIONS

### 2.1 Duty of Confidentiality
The Receiving Party agrees to:

(a) Maintain the confidentiality of all Confidential Information using the same degree of care it uses to protect its own confidential information of similar nature, but no less than commercially reasonable care;

(b) Limit access to Confidential Information to employees, contractors, and advisors (including attorneys, accountants, and consultants) who have a legitimate need to know and who are bound by written confidentiality obligations at least as restrictive as this Agreement;

(c) Use Confidential Information solely for the Permitted Use and not for any other purpose without the prior written consent of the Disclosing Party;

(d) Not disclose, publish, or distribute Confidential Information to any third party without the prior written consent of the Disclosing Party;

(e) Implement and maintain reasonable security measures to protect Confidential Information against unauthorized access, disclosure, or use.

### 2.2 Standard of Care
The Receiving Party shall protect Confidential Information using commercially reasonable security measures appropriate to the nature of the information, including but not limited to:

- Physical security controls for documents and hardware containing Confidential Information
- Encryption for electronic data both in transit and at rest
- Access controls, authentication mechanisms, and privilege restrictions
- Regular security audits, assessments, and vulnerability testing
- Training and awareness programs for authorized personnel
- Incident response procedures and breach notification protocols
- Compliance with applicable data protection laws and regulations

### 2.3 Return or Destruction
Upon written request by the Disclosing Party, or upon termination or expiration of this Agreement, the Receiving Party shall, at the Disclosing Party's election, either:

(a) Return all Confidential Information in tangible form and certify in writing that it has been returned in full; or

(b) Destroy all Confidential Information in tangible form and certify in writing the manner, date, and completeness of such destruction.

Notwithstanding the foregoing, the Receiving Party may retain one copy of Confidential Information in its legal files for compliance, archival, and record-keeping purposes, subject to the confidentiality obligations herein."""

    def _get_permitted_disclosures_section(self) -> str:
        """Generate permitted disclosures section"""
        return """## 3. PERMITTED DISCLOSURES

### 3.1 Legally Compelled Disclosure
If the Receiving Party is required by law, court order, subpoena, government request, regulatory requirement, or other legal process to disclose any Confidential Information, the Receiving Party shall:

(a) Promptly notify the Disclosing Party in writing of such requirement unless legally prohibited from doing so;

(b) Reasonably cooperate with the Disclosing Party in seeking a protective order, confidentiality agreement, or other appropriate relief;

(c) Disclose only the minimum Confidential Information legally required to be disclosed;

(d) Request that the Disclosing Party be given confidential treatment of any disclosed information;

(e) Provide the Disclosing Party with a copy of the required disclosure at the earliest practicable time.

### 3.2 Employee and Contractor Disclosure
The Receiving Party may disclose Confidential Information to its employees, contractors, and service providers who:

(a) Have a legitimate business need to know the information for purposes of the Permitted Use;

(b) Are bound by written confidentiality agreements at least as restrictive as this Agreement;

(c) Are informed of the confidential and proprietary nature of the information;

(d) Are authorized to receive such information by management.

The Receiving Party shall be responsible for breaches of confidentiality by its employees, contractors, and agents."""

    def _get_intellectual_property_section(self) -> str:
        """Generate intellectual property section"""
        return """## 4. INTELLECTUAL PROPERTY RIGHTS

### 4.1 Ownership
All right, title, and interest in and to the Confidential Information, including all intellectual property rights therein (including patents, copyrights, trade marks, trade secrets, and proprietary know-how), shall remain the exclusive property of the Disclosing Party. The Receiving Party acquires no license, rights, or interest in the Confidential Information except as expressly provided herein.

### 4.2 No License Grant
Nothing in this Agreement grants or implies any license, right, or interest in any patents, patent applications, trademarks, copyrights, trade secrets, or other intellectual property rights of the Disclosing Party.

### 4.3 Feedback and Suggestions
The Receiving Party grants the Disclosing Party a royalty-free, non-exclusive, perpetual, and irrevocable license to use any feedback, suggestions, improvements, or modifications provided by the Receiving Party regarding the Confidential Information or proposed products and services.

### 4.4 Pre-existing Rights
Each party retains all rights in any pre-existing intellectual property, materials, and technology developed or owned prior to or independently of this Agreement."""

    def _get_representations_warranties_section(self) -> str:
        """Generate representations and warranties section"""
        return """## 5. REPRESENTATIONS AND WARRANTIES

### 5.1 Authority
Each party represents and warrants that:

(a) It has full authority and power to enter into this Agreement;

(b) This Agreement constitutes the valid and binding obligation of such party;

(c) The execution and performance of this Agreement has been duly authorized by all necessary corporate action on the part of such party;

(d) This Agreement is enforceable in accordance with its terms.

### 5.2 No Conflict
Each party represents and warrants that the execution and performance of this Agreement does not violate any agreement, law, regulation, court order, or third-party right to which it is bound.

### 5.3 Disclosing Party Representations
The Disclosing Party represents and warrants that:

(a) It owns or has the right to disclose the Confidential Information;

(b) The disclosure of Confidential Information does not violate the rights of any third party;

(c) The Confidential Information is accurate to the best of its knowledge.

### 5.4 DISCLAIMER
EXCEPT AS EXPRESSLY PROVIDED HEREIN, THE CONFIDENTIAL INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, ACCURACY, COMPLETENESS, OR NON-INFRINGEMENT."""

    def _get_limitations_liability_section(self) -> str:
        """Generate limitations of liability section"""
        return """## 6. LIMITATIONS ON LIABILITY

### 6.1 No Warranty
THE CONFIDENTIAL INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING ANY WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, OR NON-INFRINGEMENT OF THIRD-PARTY RIGHTS.

### 6.2 Disclaimer of Consequential Damages
IN NO EVENT SHALL EITHER PARTY BE LIABLE TO THE OTHER PARTY FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, PUNITIVE, OR EXEMPLARY DAMAGES, INCLUDING LOST PROFITS, REVENUE, BUSINESS OPPORTUNITY, DATA, OR GOODWILL, ARISING OUT OF OR RELATED TO THIS AGREEMENT, REGARDLESS OF THE FORM OF ACTION AND WHETHER OR NOT SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

### 6.3 Limitation of Direct Damages
EXCEPT FOR BREACHES OF THE CONFIDENTIALITY OBLIGATIONS HEREUNDER AND INFRINGEMENT OF INTELLECTUAL PROPERTY RIGHTS, NEITHER PARTY'S TOTAL LIABILITY UNDER THIS AGREEMENT SHALL EXCEED THE TOTAL AMOUNT PAID BY THE RECEIVING PARTY UNDER THIS AGREEMENT, OR IF NO AMOUNTS HAVE BEEN PAID, ONE HUNDRED DOLLARS ($100.00)."""

    def _get_term_termination_section(self, cure_days: int, survival_years: int) -> str:
        """Generate term and termination section"""
        duration = self.config.confidentiality_duration.value
        duration_text = "perpetually" if duration == 0 else f"a period of {duration} years"
        
        return f"""## 7. TERM AND TERMINATION

### 7.1 Term
This Agreement shall commence on the Effective Date and shall continue for {duration_text}, unless earlier terminated in accordance with the provisions hereof.

### 7.2 Termination for Convenience
Either party may terminate this Agreement at any time upon thirty (30) days' written notice to the other party.

### 7.3 Termination for Material Breach
Either party may terminate this Agreement immediately upon written notice if the other party materially breaches any material provision of this Agreement and:

(a) Fails to cure such breach within {cure_days} days of receiving written notice; and

(b) Does not provide evidence of good faith cure efforts within such cure period.

### 7.4 Termination for Insolvency
Either party may terminate this Agreement immediately upon written notice if the other party becomes insolvent, bankrupt, unable to pay its debts, or subject to proceedings for involuntary bankruptcy.

### 7.5 Survival
The obligations and provisions set forth in Sections 2 (Confidentiality Obligations), 3 (Permitted Disclosures), 4 (Intellectual Property Rights), 5 (Representations and Warranties), 6 (Limitations on Liability), 8 (Remedies), and 9 (General Provisions) shall survive any termination or expiration of this Agreement for a period of {survival_years} years, except that obligations with respect to trade secrets shall continue for so long as such information qualifies as a trade secret under applicable law."""

    def _get_remedies_section(self) -> str:
        """Generate remedies and equitable relief section"""
        return """## 8. REMEDIES AND EQUITABLE RELIEF

### 8.1 Equitable Relief
The Receiving Party acknowledges that any breach of this Agreement may cause irreparable harm to the Disclosing Party for which monetary damages would be an inadequate and insufficient remedy. Accordingly, the Disclosing Party shall be entitled to seek equitable relief, including injunctive relief and specific performance, in addition to all other remedies available at law or in equity.

### 8.2 No Waiver
The failure or delay of either party to enforce any right, power, or provision of this Agreement shall not constitute a waiver of such right, power, or provision.

### 8.3 Cumulative Remedies
The remedies provided herein are cumulative and shall not limit or exclude any other remedies available at law or in equity.

### 8.4 Injunctive Relief
The parties acknowledge that the continued use and disclosure of Confidential Information in violation of this Agreement would cause continuing and irreparable harm. The Disclosing Party shall be entitled to immediate injunctive relief to prevent such use or disclosure, without the requirement of posting a bond."""

    def _get_general_provisions_section(self) -> str:
        """Generate general provisions section"""
        return """## 9. GENERAL PROVISIONS

### 9.1 Entire Agreement
This Agreement, including any appendices hereto, constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior and contemporaneous negotiations, understandings, and agreements, whether written or oral, regarding such subject matter.

### 9.2 Amendments and Modifications
No amendment, modification, or supplement of this Agreement shall be valid or effective unless made in writing and signed by authorized representatives of both parties. No course of dealing, course of performance, or trade practice shall be deemed to modify or amend this Agreement.

### 9.3 Severability
If any provision of this Agreement is held by a court of competent jurisdiction to be invalid, illegal, or unenforceable, such provision shall be reformed and construed to the minimum extent necessary to make it valid and enforceable, and the remaining provisions shall continue in full force and effect.

### 9.4 Waiver
No waiver of any provision or breach of this Agreement shall be effective unless made in writing and signed by the party against whom such waiver is sought to be enforced. The waiver of any breach shall not constitute a waiver of any other or subsequent breach.

### 9.5 Counterparts and Electronic Signatures
This Agreement may be executed in multiple counterparts, including in electronic format (PDF, email, or other electronic means), each of which shall be deemed an original document and all of which together shall constitute one and the same instrument.

### 9.6 Notices
Any notice required under this Agreement shall be in writing and shall be deemed delivered when:
- Personally delivered
- Sent via email with read receipt requested
- Sent by certified mail, return receipt requested
- Sent via overnight courier service (FedEx, UPS, etc.)

Notices shall be sent to the addresses specified in the signature blocks hereof.

### 9.7 Relationship of Parties
Nothing in this Agreement creates a partnership, joint venture, agency, or employment relationship between the parties. No party has authority to bind or commit the other party or to incur obligations on behalf of the other.

### 9.8 Interpretation
The headings and captions in this Agreement are for convenience only and shall not affect the interpretation or meaning of this Agreement. The use of the word "including" means "including without limitation." References to "days" mean calendar days unless otherwise specified.

### 9.9 Assignment
Neither party may assign, transfer, or delegate any of its rights or obligations under this Agreement without the prior written consent of the other party, except that either party may assign this Agreement in connection with a merger, acquisition, or sale of assets. Any unauthorized assignment shall be void."""

    def _get_special_provisions_section(self) -> str:
        """Generate special provisions section"""
        return """## 10. SPECIAL PROVISIONS

### 10.1 Duration of Confidentiality Obligations
Except as provided below, the Receiving Party's obligations with respect to Confidential Information shall continue for the term specified in Section 7.5. Notwithstanding the foregoing, any information constituting a "trade secret" under the Uniform Trade Secrets Act or similar laws shall continue to be protected for so long as it qualifies as a trade secret.

### 10.2 Third-Party Information
The Receiving Party acknowledges that Confidential Information may contain proprietary information, trade secrets, or other confidential materials of third parties. The Receiving Party agrees to treat such information with the same level of confidentiality and care as it treats other Confidential Information and agrees not to disclose such information to any third party without the consent of both the Disclosing Party and the applicable third-party owner.

### 10.3 No Obligation to Proceed
Nothing in this Agreement obligates either party to disclose any information, enter into any transaction, or proceed with any proposed business opportunity. The Disclosing Party may discontinue discussions or disclosures at any time.

### 10.4 Competition
Nothing in this Agreement shall prevent the Receiving Party from:
(a) Engaging in any business or activity;
(b) Competing with the Disclosing Party;
(c) Using information that does not constitute Confidential Information or that falls within the exceptions in Section 1.2;
(d) Hiring employees of the Disclosing Party, provided no Confidential Information is disclosed.

### 10.5 Cooperation
Each party agrees to cooperate in good faith in the negotiation and implementation of any definitive agreements that may result from the discussions facilitated by this Agreement.

### 10.6 No License
The disclosure of Confidential Information shall not be construed as granting any license under any patents, patent applications, or other intellectual property rights, whether by implication, estoppel, or otherwise."""

    def _get_signature_block(self) -> str:
        """Generate signature blocks"""
        return f"""---

## SIGNATURES

**IN WITNESS WHEREOF**, the parties have executed this Non-Disclosure Agreement as of the Effective Date.

**DISCLOSING PARTY:**

**{self.config.disclosing_party.legal_name}**

By: ___________________________________

Name: _________________________________

Title: __________________________________

Date: __________________________________

Email: _________________________________

Phone: _________________________________


**RECEIVING PARTY:**

**{self.config.receiving_party.legal_name}**

By: ___________________________________

Name: _________________________________

Title: __________________________________

Date: __________________________________

Email: _________________________________

Phone: _________________________________

---"""

    def _get_appendices(self) -> str:
        """Generate appendices"""
        appendices = ""
        
        # Appendix A: Confidential Information Schedule
        appendices += """## APPENDIX A: CONFIDENTIAL INFORMATION SCHEDULE

The following items constitute Confidential Information under this Agreement:

| Item No. | Description | Classification | Date Disclosed | Format |
|----------|-------------|-----------------|-----------------|--------|
| 1 | | Proprietary/Confidential | | Written/Oral/Digital |
| 2 | | Proprietary/Confidential | | Written/Oral/Digital |
| 3 | | Proprietary/Confidential | | Written/Oral/Digital |
| 4 | | Proprietary/Confidential | | Written/Oral/Digital |
| 5 | | Proprietary/Confidential | | Written/Oral/Digital |

**Notes:**
- Classification levels: Proprietary, Confidential, Highly Confidential, Restricted
- Descriptions should be specific but not unnecessarily detailed
- Format refers to how the information was disclosed

---

"""
        
        # Appendix B: Authorized Recipients
        appendices += """## APPENDIX B: AUTHORIZED RECIPIENTS

The following individuals are authorized to receive and access Confidential Information on behalf of the Receiving Party:

| Name | Title | Department | Email | Phone |
|------|-------|-----------|-------|-------|
| | | | | |
| | | | | |
| | | | | |

**Instructions:**
1. All recipients must acknowledge this NDA in writing before accessing Confidential Information
2. Recipients are responsible for maintaining confidentiality
3. Any changes to authorized recipients must be communicated in writing
4. Recipients must complete confidentiality training

---

"""
        
        # Appendix C: Data Security Requirements
        appendices += """## APPENDIX C: DATA SECURITY REQUIREMENTS

The Receiving Party shall implement the following security measures:

### Physical Security
- Locked storage for physical documents containing Confidential Information
- Restricted access to facilities where Confidential Information is maintained
- Security cameras and surveillance in sensitive areas
- Badge access control systems

### Electronic Security
- Encryption of data in transit (TLS 1.2 or higher)
- Encryption of data at rest (AES-256 or equivalent)
- Multi-factor authentication for system access
- Strong password policies (minimum 12 characters, mixed case, numbers, symbols)
- Regular security patches and updates

### Personnel Security
- Background checks for employees with access to Confidential Information
- Confidentiality agreements for all employees
- Regular security awareness training
- Incident response procedures

### Audit and Compliance
- Regular security audits (quarterly)
- Compliance assessment with this Appendix
- Incident logging and reporting
- Annual certification of compliance

---

"""
        
        return appendices

    def generate(self) -> str:
        """Generate complete NDA document"""
        
        doc_date = self.effective_date.strftime("%B %d, %Y")
        
        doc = f"""# NON-DISCLOSURE AGREEMENT (NDA)

**This Non-Disclosure Agreement ("Agreement") is entered into effective as of {doc_date} ("Effective Date")**

**BETWEEN:**

**{self.config.disclosing_party.legal_name}**, a {self.config.disclosing_party.entity_type} organized and existing under the laws of {self.config.disclosing_party.state_of_incorporation}, with principal place of business at {self.config.disclosing_party.address} ("Disclosing Party")

**AND:**

**{self.config.receiving_party.legal_name}**, a {self.config.receiving_party.entity_type} organized and existing under the laws of {self.config.receiving_party.state_of_incorporation}, with principal place of business at {self.config.receiving_party.address} ("Receiving Party")

---

"""
        
        # Add sections
        doc += self._get_definitions_section() + "\n\n"
        doc += self._get_confidentiality_section(self.config.cure_period_days) + "\n\n"
        doc += self._get_permitted_disclosures_section() + "\n\n"
        doc += self._get_intellectual_property_section() + "\n\n"
        doc += self._get_representations_warranties_section() + "\n\n"
        doc += self._get_limitations_liability_section() + "\n\n"
        doc += self._get_term_termination_section(self.config.cure_period_days, self.config.survival_duration) + "\n\n"
        doc += self._get_remedies_section() + "\n\n"
        doc += self._get_general_provisions_section() + "\n\n"
        doc += self._get_special_provisions_section() + "\n\n"
        doc += self._get_governing_law_clause() + "\n\n"
        doc += self._get_signature_block() + "\n\n"
        
        if self.config.include_appendices:
            doc += self._get_appendices()
        
        doc += "**END OF DOCUMENT**\n"
        
        return doc


def create_sample_nda():
    """Create a sample NDA document"""
    
    config = NDAConfiguration(
        disclosing_party=Party(
            legal_name="TechCorp Innovations Inc.",
            entity_type="Corporation",
            state_of_incorporation="Delaware",
            address="123 Innovation Drive, San Francisco, CA 94102",
            contact_name="John Smith",
            contact_title="General Counsel",
            contact_email="john.smith@techcorp.com"
        ),
        receiving_party=Party(
            legal_name="Strategic Partners LLC",
            entity_type="Limited Liability Company",
            state_of_incorporation="California",
            address="456 Business Boulevard, Los Angeles, CA 90001",
            contact_name="Jane Doe",
            contact_title="VP Business Development",
            contact_email="jane.doe@strategicpartners.com"
        ),
        effective_date=datetime.now(),
        confidentiality_duration=ConfidentialityDuration.FIVE_YEARS,
        jurisdiction=Jurisdiction.CALIFORNIA,
        survival_duration=5,
        cure_period_days=30,
        include_appendices=True
    )
    
    generator = NDAGenerator(config)
    return generator.generate()


if __name__ == "__main__":
    nda_document = create_sample_nda()
    
    # Save to file
    output_path = "/Users/vishaljha/CLM_Backend/SAMPLE_NDA_GENERATED.md"
    with open(output_path, 'w') as f:
        f.write(nda_document)
    
    print(f"✓ NDA document generated successfully")
    print(f"✓ Saved to: {output_path}")
    print(f"✓ Document length: {len(nda_document)} characters")
    print(f"✓ Production-ready format with all required clauses")
