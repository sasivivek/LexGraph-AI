"""
Sample Data — Representative legal data from the Companies Act 2013,
Corporate Laws (Amendment) Act 2026, and Companies Rules 2014.

This structured data serves as the primary data source for the knowledge graph,
representing key provisions across the three legal documents.
"""

act_data = {
    "name": "Companies Act",
    "year": 2013,
    "fullTitle": "The Companies Act, 2013",
    "dateEnacted": "2013-08-29",
    "shortDescription": "An Act to consolidate and amend the law relating to companies.",
    "parts": [
        {
            "number": "I",
            "title": "Preliminary",
            "sections": [
                {
                    "number": 1,
                    "title": "Short title, extent, commencement and application",
                    "text": "(1) This Act may be called the Companies Act, 2013. (2) It extends to the whole of India. (3) It shall come into force on such date as the Central Government may, by notification in the Official Gazette, appoint.",
                },
                {
                    "number": 2,
                    "title": "Definitions",
                    "text": "In this Act, unless the context otherwise requires,—",
                    "subsections": [
                        {"number": 6, "text": '"associate company", in relation to another company, means a company in which that other company has a significant influence, but which is not a subsidiary company of the company having such influence and includes a joint venture company.'},
                        {"number": 20, "text": '"company" means a company incorporated under this Act or under any previous company law.'},
                        {"number": 22, "text": '"company limited by guarantee" means a company having the liability of its members limited by the memorandum to such amount as the members may respectively undertake to contribute to the assets of the company in the event of its being wound up.'},
                        {"number": 28, "text": '"cost accountant" means a cost accountant as defined in clause (b) of sub-section (1) of section 2 of the Cost and Works Accountants Act, 1959.'},
                        {"number": 30, "text": '"debenture" includes debenture stock, bonds or any other instrument of a company evidencing a debt, whether constituting a charge on the assets of the company or not.'},
                        {"number": 35, "text": '"director" means a director appointed to the Board of a company.'},
                        {"number": 40, "text": '"financial statement", in relation to a company, includes balance sheet, profit and loss account or income and expenditure account, cash flow statement, statement of changes in equity.'},
                        {"number": 46, "text": '"holding company", in relation to one or more other companies, means a company of which such companies are subsidiary companies.'},
                        {"number": 51, "text": '"key managerial personnel", in relation to a company, means the Chief Executive Officer or the managing director or the manager, the company secretary, the whole-time director, the Chief Financial Officer.'},
                        {"number": 68, "text": '"private company" means a company having a minimum paid-up share capital as may be prescribed, which by its articles restricts the right to transfer its shares, limits the number of its members to two hundred.'},
                        {"number": 71, "text": '"public company" means a company which is not a private company.'},
                        {"number": 76, "text": '"related party", with reference to a company, means a director or his relative, a key managerial personnel or his relative, a firm or private company in which a director, manager or his relative is a partner or member.'},
                        {"number": 85, "text": '"small company" means a company, other than a public company, whose paid-up share capital does not exceed fifty lakh rupees or such higher amount as may be prescribed.'},
                        {"number": 87, "text": '"subsidiary company" or "subsidiary", in relation to any other company, means a company in which the holding company controls the composition of the Board of Directors or exercises or controls more than one-half of the total voting power.'},
                    ],
                },
            ],
        },
        {
            "number": "II",
            "title": "Incorporation of Company and Matters Incidental Thereto",
            "sections": [
                {"number": 3, "title": "Formation of company", "text": "(1) A company may be formed for any lawful purpose by— (a) seven or more persons, where the company to be formed is to be a public company; (b) two or more persons, where the company to be formed is to be a private company; (c) one person, where the company to be formed is to be One Person Company. (2) A company formed under sub-section (1) may be either— (a) a company limited by shares; or (b) a company limited by guarantee; or (c) an unlimited company."},
                {"number": 4, "title": "Memorandum of Association", "text": '(1) The memorandum of every company shall state— (a) the name of the company with the last word "Limited" in the case of a public limited company, or the last words "Private Limited" in the case of a private limited company; (b) the State in which the registered office of the company is to be situated; (c) the objects for which the company is proposed to be incorporated. (2) The memorandum of a company limited by shares shall also state the amount of share capital and the division thereof into shares of a fixed amount.'},
                {"number": 5, "title": "Articles of Association", "text": "(1) The articles of a company shall contain the regulations for management of the company. (2) The articles shall also contain such matters, as may be prescribed. (3) The articles may contain provisions for entrenchment."},
                {"number": 7, "title": "Incorporation of company", "text": "(1) There shall be filed with the Registrar within whose jurisdiction the registered office of a company is proposed to be situated, the following documents and information for registration, namely:— (a) the memorandum and articles of the company; (b) a declaration in the prescribed form by an advocate, a chartered accountant, cost accountant or company secretary in practice; (c) an affidavit from each of the subscribers to the memorandum; (d) the address for correspondence till its registered office is established; (e) the particulars of each person mentioned in the articles as the first director of the company; (f) the particulars of the interests of the persons mentioned in the articles as the first directors of the company."},
                {"number": 8, "title": "Formation of companies with charitable objects, etc.", "text": "(1) Where it is proved to the satisfaction of the Central Government that a person or an association of persons proposed to be registered under this Act as a limited company— (a) has in its objects the promotion of commerce, art, science, sports, education, research, social welfare, religion, charity, protection of environment, or any such other object; (b) intends to apply its profits, if any, or other income in promoting its objects; and (c) intends to prohibit the payment of any dividend to its members."},
                {"number": 12, "title": "Registered office of company", "text": "(1) A company shall, on and from the fifteenth day of its incorporation and at all times thereafter, have a registered office capable of receiving and acknowledging all communications and notices as may be addressed to it. (2) The company shall furnish to the Registrar verification of its registered office within a period of thirty days of its incorporation."},
            ],
        },
        {
            "number": "III",
            "title": "Prospectus and Allotment of Securities",
            "sections": [
                {"number": 23, "title": "Public offer and private placement", "text": "(1) A public company may issue securities— (a) to public through prospectus by complying with the provisions of Part I of this Chapter; or (b) through private placement by complying with the provisions of Part II of this Chapter. (2) A private company may issue securities— (a) by way of rights issue or bonus issue; (b) through private placement by complying with the provisions of Part II of this Chapter."},
                {"number": 26, "title": "Matters to be stated in prospectus", "text": "(1) Every prospectus issued by or on behalf of a public company either with reference to its formation or subsequently, or by or on behalf of any person who is or has been engaged or interested in the formation of a public company, shall be dated and signed and shall state such information and set out such reports on financial information as may be specified by the Securities and Exchange Board."},
                {"number": 39, "title": "Allotment of securities by company", "text": "(1) Where a company having a share capital makes any allotment of securities, the company shall file with the Registrar a return of allotment in the prescribed form within thirty days. (2) Whenever a company having share capital makes any allotment of securities, it shall file with the Registrar a return of allotment within prescribed time."},
                {"number": 42, "title": "Offer or invitation for subscription of securities on private placement", "text": "(1) A company may, subject to the provisions of this section, make a private placement of securities. (2) A private placement shall be made only to a select group of persons who have been identified by the Board of Directors."},
            ],
        },
        {
            "number": "IV",
            "title": "Share Capital and Debentures",
            "sections": [
                {"number": 43, "title": "Kinds of share capital", "text": "The share capital of a company limited by shares shall be of two kinds, namely:— (a) equity share capital— (i) with voting rights; or (ii) with differential rights as to dividend, voting or otherwise in accordance with such rules as may be prescribed; and (b) preference share capital."},
                {"number": 47, "title": "Voting rights", "text": "(1) Subject to the provisions of section 43 and sub-section (2) of section 50, every member of a company limited by shares and holding equity share capital therein, shall have a right to vote on every resolution placed before the company. (2) On a poll, the voting rights of a member holding equity share capital shall be in proportion to his share in the paid-up equity share capital of the company."},
                {"number": 52, "title": "Application of premiums received on issue of shares", "text": '(1) Where a company issues shares at a premium, whether for cash or otherwise, a sum equal to the aggregate amount of the premium received on those shares shall be transferred to a "securities premium account".'},
                {"number": 54, "title": "Sub-division and consolidation of share capital", "text": "(1) A limited company having a share capital may, if so authorized by its articles, alter the conditions of its memorandum as follows:— (a) increase its share capital by such amount as it thinks expedient; (b) consolidate and divide all or any of its share capital into shares of a larger amount than its existing shares; (c) convert all or any of its fully paid-up shares into stock."},
                {"number": 62, "title": "Further issue of share capital", "text": "(1) Where at any time, a company having a share capital proposes to increase its subscribed capital by the issue of further shares, such shares shall be offered— (a) to persons who, at the date of the offer, are holders of equity shares of the company in proportion to the paid-up share capital on those shares by sending a letter of offer."},
                {"number": 68, "title": "Power of company to purchase its own securities", "text": "(1) No company limited by shares or by guarantee and having a share capital shall have the power to buy its own shares, unless the consequent reduction of share capital is effected by following the provisions of section 66. (2) Notwithstanding anything contained in sub-section (1), a company may purchase its own shares or other specified securities out of its free reserves, securities premium account or the proceeds of the issue of any shares or other specified securities."},
            ],
        },
        {
            "number": "VII",
            "title": "Management and Administration",
            "sections": [
                {"number": 96, "title": "Annual general meeting", "text": "(1) Every company other than a One Person Company shall in each year hold in addition to any other meetings, a general meeting as its annual general meeting and shall specify the meeting as such in the notices calling it. (2) Every annual general meeting shall be called during business hours on any day that is not a National Holiday and shall be held either at the registered office of the company or at some other place within the city, town or village in which the registered office of the company is situate."},
                {"number": 100, "title": "Calling of extraordinary general meeting", "text": "(1) The Board of Directors of a company may call an extraordinary general meeting of the company at any time. (2) The Board of Directors shall, at the requisition made by the specified number of members, call an extraordinary general meeting of the company within the prescribed time."},
                {"number": 117, "title": "Resolutions and agreements to be filed", "text": "(1) A copy of every resolution or any agreement, in respect of matters specified in sub-section (3) together with the explanatory statement under section 102, if any, annexed to the notice calling the meeting in which the resolution is proposed, shall be filed with the Registrar within thirty days of the passing or making thereof in such manner and with such fees as may be prescribed."},
            ],
        },
        {
            "number": "VIII",
            "title": "Declaration and Payment of Dividend",
            "sections": [
                {"number": 123, "title": "Declaration of dividend", "text": "(1) No dividend shall be declared or paid by a company for any financial year except out of the profits of the company for that year arrived at after providing for depreciation in accordance with the provisions of sub-section (2), or out of the profits of the company for any previous financial year or years arrived at after providing for depreciation in accordance with the provisions of that sub-section and remaining undistributed, or out of both. (2) Depreciation shall be provided in accordance with the provisions of Schedule II."},
                {"number": 124, "title": "Unpaid dividend account", "text": "(1) Where a dividend has been declared by a company but has not been paid or claimed within thirty days from the date of the declaration to any shareholder entitled to the payment of the dividend, the company shall, within seven days from the date of expiry of the said period of thirty days, transfer the total amount of dividend which remains unpaid or unclaimed to a special account to be opened by the company in that behalf in any scheduled bank to be called the Unpaid Dividend Account."},
                {"number": 127, "title": "Punishment for failure to distribute dividends", "text": "Where a dividend has been declared by a company but has not been paid or the warrant in respect thereof has not been posted within thirty days from the date of declaration to any shareholder entitled to the payment of the dividend, every director of the company shall, if he is knowingly a party to the default, be punishable with imprisonment which may extend to two years and with fine."},
            ],
        },
        {
            "number": "X",
            "title": "Audit and Auditors",
            "sections": [
                {"number": 139, "title": "Appointment of auditors", "text": "(1) Subject to the provisions of this Chapter, every company shall, at the first annual general meeting, appoint an individual or a firm as an auditor who shall hold office from the conclusion of that meeting till the conclusion of its sixth annual general meeting and thereafter till the conclusion of every sixth meeting."},
                {"number": 140, "title": "Removal, resignation of auditor and giving of special notice", "text": "(1) The auditor appointed under section 139 may be removed from his office before the expiry of his term only by a special resolution of the company, after obtaining the previous approval of the Central Government in that behalf."},
                {"number": 143, "title": "Powers and duties of auditors and auditing standards", "text": "(1) Every auditor of a company shall have a right of access at all times to the books of account and vouchers of the company, whether kept at the registered office of the company or at any other place and shall be entitled to require from the officers of the company such information and explanation as he may consider necessary for the performance of his duties as auditor."},
                {"number": 147, "title": "Punishment for contravention", "text": "(1) If any of the provisions of sections 139 to 146 is contravened, the company shall be punishable with fine which shall not be less than twenty-five thousand rupees but which may extend to five lakh rupees and every officer of the company who is in default shall be punishable with imprisonment for a term which may extend to one year or with fine."},
            ],
        },
        {
            "number": "XI",
            "title": "Appointment and Qualifications of Directors",
            "sections": [
                {"number": 149, "title": "Company to have Board of Directors", "text": "(1) Every company shall have a Board of Directors consisting of individuals as directors and shall have— (a) a minimum number of three directors in the case of a public company, (b) a minimum number of two directors in the case of a private company, and (c) a minimum number of one director in the case of a One Person Company. (2) Every company shall have at least one director who has stayed in India for a total period of not less than one hundred and eighty-two days in the previous calendar year."},
                {"number": 150, "title": "Manner of selection of independent directors and maintenance of databank of independent directors", "text": "(1) An independent director may be selected from a data bank maintained by anybody, institute or association as may be notified by the Central Government."},
                {"number": 152, "title": "Appointment of directors", "text": "(1) Every director shall be appointed by the company in general meeting. (2) This section shall not apply to the appointment of the first director in the case of a One Person Company."},
                {"number": 161, "title": "Appointment of additional director, alternate director and nominee director", "text": "(1) The articles of a company may confer on its Board of Directors the power to appoint any person, other than a person who fails to get appointed as a director in a general meeting, as an additional director at any time who shall hold office up to the date of the next annual general meeting."},
                {"number": 164, "title": "Disqualifications for appointment of director", "text": "(1) A person shall not be eligible for appointment as a director of a company, if— (a) he is of unsound mind and stands so declared by a competent court; (b) he is an undischarged insolvent; (c) he has applied to be adjudicated as an insolvent and his application is pending; (d) he has been convicted of any offence involving moral turpitude or otherwise, and sentenced in respect thereof to imprisonment for not less than six months."},
                {"number": 166, "title": "Duties of directors", "text": "(1) Subject to the provisions of this Act, a director of a company shall act in accordance with the articles of the company. (2) A director of a company shall act in good faith in order to promote the objects of the company for the benefit of its members as a whole, and in the best interests of the company, its employees, the shareholders, the community and for the protection of environment."},
            ],
        },
        {
            "number": "XII",
            "title": "Meetings of Board and its Powers",
            "sections": [
                {"number": 173, "title": "Meetings of Board", "text": "(1) Every company shall hold the first meeting of the Board of Directors within thirty days of the date of its incorporation. (2) Every company shall hold a minimum number of four meetings of its Board of Directors every year in such a manner that not more than one hundred and twenty days shall intervene between two consecutive meetings of the Board."},
                {"number": 177, "title": "Audit Committee", "text": "(1) The Board of Directors of every listed company and such other class or classes of companies, as may be prescribed, shall constitute an Audit Committee. (2) The Audit Committee shall consist of a minimum of three directors with independent directors forming a majority."},
                {"number": 178, "title": "Nomination and Remuneration Committee and Stakeholders Relationship Committee", "text": "(1) The Board of Directors of every listed company and such other class or classes of companies, as may be prescribed, shall constitute a Nomination and Remuneration Committee. (2) The Nomination and Remuneration Committee shall consist of three or more non-executive directors out of which not less than one-half shall be independent directors."},
                {"number": 179, "title": "Powers of Board", "text": "(1) The Board of Directors of a company shall be entitled to exercise all such powers, and to do all such acts and things, as the company is authorised to exercise and do. (2) No regulation made by the company in general meeting shall invalidate any prior act of the Board which would have been valid if that regulation had not been made."},
                {"number": 185, "title": "Loan to directors, etc.", "text": "(1) No company shall, directly or indirectly, advance any loan, including any loan represented by a book debt, to any director of the company or of a company which is its holding company or any partner or relative of any such director, or give any guarantee or provide any security in connection with any loan taken by any such director or such other person. (2) A company may advance any loan including any loan represented by a book debt, or give any guarantee or provide any security in connection with any loan taken by any director of such company subject to the condition that a special resolution is passed by the company in general meeting."},
                {"number": 186, "title": "Loan and investment by company", "text": "(1) Without prejudice to the provisions contained in this Act, a company shall unless otherwise prescribed, make investment through not more than two layers of investment companies. (2) No company shall directly or indirectly, give any loan to any person or other body corporate or give any guarantee or provide security in connection with a loan to any other body corporate or person or acquire by way of subscription, purchase or otherwise, the securities of any other body corporate, exceeding sixty per cent of its paid-up share capital, free reserves and securities premium account or one hundred per cent of its free reserves and securities premium account, whichever is more."},
            ],
        },
        {
            "number": "XIII",
            "title": "Appointment and Remuneration of Managerial Personnel",
            "sections": [
                {"number": 196, "title": "Appointment of managing director, whole-time director or manager", "text": "(1) No company shall appoint or employ at the same time a managing director and a manager. (2) No company shall appoint or re-appoint any person as its managing director, whole-time director or manager for a term exceeding five years at a time. (3) No company shall appoint or re-appoint any person as its managing director, whole-time director or manager who is below the age of twenty-one years or who has attained the age of seventy years."},
                {"number": 197, "title": "Overall maximum managerial remuneration and managerial remuneration in case of absence or inadequacy of profits", "text": "(1) The total managerial remuneration payable by a public company, to its directors, including managing director and whole-time director, and its manager in respect of any financial year shall not exceed eleven per cent of the net profits of that company for that financial year computed in the manner laid down in section 198."},
                {"number": 203, "title": "Appointment of key managerial personnel", "text": "(1) Every company belonging to such class or classes of companies as may be prescribed shall have whole-time key managerial personnel. (2) Every whole-time key managerial personnel of a company shall be appointed by means of a resolution of the Board containing the terms and conditions of the appointment including the remuneration."},
            ],
        },
        {
            "number": "XIV",
            "title": "Inspection, Inquiry and Investigation",
            "sections": [
                {"number": 206, "title": "Power to call for information, inspect books and conduct inquiries", "text": "(1) Where the Registrar is satisfied that any complaint received from any member, or creditor, or any other person, has substance, or on the basis of information or documents available with him, the Registrar may— (a) call on the company to furnish such information or explanation within such reasonable time as he may specify."},
                {"number": 210, "title": "Investigation into affairs of company", "text": "(1) Where the Central Government is of the opinion that it is necessary to investigate into the affairs of a company,— (a) on the receipt of a report of the Registrar or inspector under section 208; (b) on intimation of a special resolution passed by a company that the affairs of the company ought to be investigated; (c) in public interest, it may order an investigation into the affairs of the company."},
            ],
        },
        {
            "number": "XX",
            "title": "Winding Up",
            "sections": [
                {"number": 270, "title": "Circumstances in which company may be wound up by Tribunal", "text": "(1) A company may, on a petition under section 272, be wound up by the Tribunal,— (a) if the company has, by special resolution, resolved that the company be wound up by the Tribunal; (b) if the company has acted against the interests of the sovereignty and integrity of India, the security of the State, friendly relations with foreign States, public order, decency or morality."},
                {"number": 271, "title": "Petition for winding up", "text": "A petition to the Tribunal for the winding up of a company shall be presented by— (a) the company; (b) any contributory or contributories; (c) all or any of the persons specified in clauses (a) and (b); (d) the Registrar; (e) any person authorised by the Central Government in that behalf; (f) in a case falling under clause (b) of section 271, by the Central Government or a State Government."},
            ],
        },
        {
            "number": "XXIX",
            "title": "Miscellaneous",
            "sections": [
                {"number": 447, "title": "Punishment for fraud", "text": "Without prejudice to any liability including repayment of any debt under this Act or any other law for the time being in force, any person who is found to be guilty of fraud, shall be punishable with imprisonment for a term which shall not be less than six months but which may extend to ten years and shall also be liable to fine which shall not be less than the amount involved in the fraud, but which may extend to three times the amount involved in the fraud."},
                {"number": 448, "title": "Punishment for false statement", "text": "If in any return, report, certificate, financial statement, prospectus, statement or other document required by, or for, the purposes of any of the provisions of this Act or the rules made thereunder, any person makes a statement, (a) which is false in any material particular, knowing it to be false; or (b) which omits any material fact, knowing it to be material, he shall be liable under section 447."},
                {"number": 462, "title": "Power of Central Government to make rules", "text": "(1) The Central Government may, by notification, make rules for carrying out the provisions of this Act. (2) In particular, and without prejudice to the generality of the foregoing power, such rules may provide for all or any of the following matters."},
                {"number": 469, "title": "Power of Central Government to amend Schedules", "text": "(1) The Central Government may, by notification, amend any of the Schedules to this Act. (2) Every notification issued under sub-section (1) shall be laid, as soon as may be, before each House of Parliament."},
                {"number": 470, "title": "Repeal and saving", "text": "(1) The Companies Act, 1956 shall stand repealed on and from the commencement of this Act. (2) Notwithstanding the repeal of the Companies Act, 1956, anything done or any action taken or purported to have been done or taken under the repealed Act shall be deemed to have been done or taken under the corresponding provisions of this Act."},
            ],
        },
    ],
}

amendment_data = {
    "name": "Corporate Laws (Amendment) Act",
    "year": 2026,
    "fullTitle": "The Corporate Laws (Amendment) Act, 2026",
    "dateEnacted": "2026-01-15",
    "shortDescription": "An Act further to amend the Companies Act, 2013 and the Limited Liability Partnership Act, 2008.",
    "amendments": [
        {
            "targetSection": 2,
            "targetSubsection": 85,
            "type": "substitution",
            "description": 'Definition of "small company" revised — threshold for paid-up capital increased from fifty lakh rupees to four crore rupees and turnover threshold increased from two crore rupees to forty crore rupees.',
            "originalText": '"small company" means a company, other than a public company, whose paid-up share capital does not exceed fifty lakh rupees or such higher amount as may be prescribed.',
            "newText": '"small company" means a company, other than a public company,— (i) paid-up share capital of which does not exceed four crore rupees or such higher amount as may be prescribed which shall not be more than ten crore rupees; and (ii) turnover of which as per profit and loss account for the immediately preceding financial year does not exceed forty crore rupees or such higher amount as may be prescribed which shall not be more than one hundred crore rupees.',
        },
        {
            "targetSection": 149,
            "targetSubsection": 1,
            "type": "substitution",
            "description": "Minimum number of directors for a public company increased and requirement for woman director expanded to include certain classes of private companies.",
            "originalText": "Every company shall have a Board of Directors consisting of individuals as directors and shall have— (a) a minimum number of three directors in the case of a public company",
            "newText": "Every company shall have a Board of Directors consisting of individuals as directors and shall have— (a) a minimum number of three directors in the case of a public company; (b) a minimum number of two directors in the case of a private company; and (c) a minimum number of one director in the case of a One Person Company. Provided that such class or classes of companies as may be prescribed, shall have at least one woman director.",
        },
        {
            "targetSection": 135,
            "type": "insertion",
            "description": "New provisions inserted for Corporate Social Responsibility (CSR) — companies meeting certain thresholds must constitute a CSR Committee and spend at least two per cent of average net profits on CSR activities.",
            "newText": "(1) Every company having net worth of rupees five hundred crore or more, or turnover of rupees one thousand crore or more or a net profit of rupees five crore or more during the immediately preceding financial year shall constitute a Corporate Social Responsibility Committee of the Board. (2) The Board shall ensure that the company spends, in every financial year, at least two per cent of the average net profits of the company made during the three immediately preceding financial years or where the company has not completed the period of three financial years since its incorporation, during such immediately preceding financial years, in pursuance of its Corporate Social Responsibility Policy.",
        },
        {
            "targetSection": 185,
            "type": "substitution",
            "description": "Restrictions on loans to directors substantially modified — conditions for permissible loans clarified and penalty provisions strengthened.",
            "originalText": "No company shall, directly or indirectly, advance any loan, including any loan represented by a book debt, to any director of the company",
            "newText": "(1) No company shall, directly or indirectly, advance any loan, including any loan represented by a book debt to, or give any guarantee or provide any security in connection with any loan taken by,— (a) any director of company, or of a company which is its holding company or any partner or relative of any such director; or (b) any firm in which any such director or relative is a partner. (2) A company may advance any loan including any loan represented by a book debt, or give any guarantee or provide any security in connection with any loan taken by any person in whom any of the director of the company is interested, subject to the condition that— (a) a special resolution is passed by the company in general meeting; (b) the loans are utilised by the borrowing company for its principal business activities.",
        },
        {
            "targetSection": 186,
            "targetSubsection": 2,
            "type": "substitution",
            "description": "Loan and investment limits revised. Threshold increased from sixty per cent to one hundred per cent of paid-up share capital.",
            "originalText": "exceeding sixty per cent of its paid-up share capital",
            "newText": "exceeding one hundred per cent of its paid-up share capital, free reserves and securities premium account or one hundred per cent of its free reserves and securities premium account, whichever is more",
        },
        {
            "targetSection": 196,
            "targetSubsection": 3,
            "type": "substitution",
            "description": "Age limit for managing director revised — upper age limit of seventy years modified with provision for appointment beyond seventy years with special resolution.",
            "originalText": "who has attained the age of seventy years",
            "newText": "who has attained the age of seventy years: Provided that the appointment of a person who has attained the age of seventy years may be made by passing a special resolution in which case the explanatory statement annexed to the notice for such motion shall indicate the justification for appointing such person",
        },
        {
            "targetSection": 42,
            "type": "substitution",
            "description": "Private placement provisions simplified — number of persons to whom offer can be made increased and reporting requirements streamlined.",
            "originalText": "A company may, subject to the provisions of this section, make a private placement of securities.",
            "newText": "(1) A company may, subject to the provisions of this section, make a private placement of securities. (2) A private placement shall be made only to a select group of persons who have been identified by the Board, whose number shall not exceed fifty or such higher number as may be prescribed, in a financial year. (3) Any offer or invitation not in compliance with this section shall be treated as a public offer and all provisions of this Act and the Securities Contracts (Regulation) Act, 1956 shall be complied with.",
        },
        {
            "targetSection": 123,
            "type": "insertion",
            "description": "New sub-section inserted allowing declaration of interim dividend and provisions for its treatment.",
            "newText": "(3) The Board of Directors of a company may declare interim dividend during any financial year or at any time during the period from closure of financial year till holding of the annual general meeting out of the surplus in the profit and loss account or out of profits of the financial year for which such interim dividend is sought to be declared or out of profits generated in the financial year till the quarter preceding the date of declaration of the interim dividend.",
        },
        {
            "targetSection": 447,
            "type": "substitution",
            "description": "Punishment for fraud enhanced — minimum imprisonment increased and provision for compounding of certain offences removed.",
            "originalText": "imprisonment for a term which shall not be less than six months but which may extend to ten years",
            "newText": "imprisonment for a term which shall not be less than one year but which may extend to ten years and shall also be liable to fine which shall not be less than the amount involved in the fraud, but which may extend to three times the amount involved in the fraud. Provided that where the fraud in question involves public interest, the term of imprisonment shall not be less than three years",
        },
        {
            "targetSection": 462,
            "targetSubsection": 1,
            "type": "insertion",
            "description": "Power of Central Government to make rules expanded to include provisions for electronic filing and digital compliance.",
            "newText": "Provided further that the Central Government may prescribe the manner and form of electronic filing, digital signatures, and such other matters relating to e-governance as may be necessary for the purposes of this Act.",
        },
    ],
}

rules_data = {
    "name": "Companies Rules",
    "year": 2014,
    "fullTitle": "The Companies (Incorporation) Rules, 2014",
    "rules": [
        {"number": "2.1", "title": "Companies (Incorporation) Rules, 2014 — Reservation of Name", "text": "An application for reservation of name shall be made in Form No. INC-1 through the web service available at www.mca.gov.in by paying the prescribed fee.", "relatedSection": 4, "category": "Incorporation"},
        {"number": "3.1", "title": "Companies (Incorporation) Rules, 2014 — Incorporation of Company", "text": "For the purposes of registration of a company, the memorandum and articles of association and other documents required to be filed under the Act shall be filed using Form No. INC-7 (for One Person Company), Form No. INC-2 (for companies other than One Person Company) along with the prescribed fee.", "relatedSection": 7, "category": "Incorporation"},
        {"number": "4.1", "title": "Companies (Incorporation) Rules, 2014 — Registered Office", "text": "Every company shall verify its registered office within thirty days of its incorporation in Form No. INC-22.", "relatedSection": 12, "category": "Incorporation"},
        {"number": "5.1", "title": "Companies (Share Capital and Debentures) Rules, 2014 — Issue of Shares", "text": "A company issuing shares with differential rights shall comply with the conditions that the articles of association of the company authorizes the issue of shares with differential rights and that the company has not defaulted in filing financial statements and annual returns for three financial years immediately preceding the financial year in which it is decided to issue such shares.", "relatedSection": 43, "category": "Share Capital"},
        {"number": "6.1", "title": "Companies (Share Capital and Debentures) Rules, 2014 — Further Issue", "text": "For the purposes of clause (a) of sub-section (1) of section 62, the notice to be sent to existing shareholders shall be dispatched through registered post or speed post or through electronic mode to all existing shareholders at least three days before the opening of the issue.", "relatedSection": 62, "category": "Share Capital"},
        {"number": "7.1", "title": "Companies (Declaration and Payment of Dividend) Rules, 2014", "text": "No company shall declare dividend unless carried over previous losses and depreciation not provided in previous year or years are set off against profit of the company of the current year.", "relatedSection": 123, "category": "Dividend"},
        {"number": "8.1", "title": "Companies (Appointment and Qualification of Directors) Rules, 2014 — Number of Directors", "text": "Every listed company shall have at least one-third of the total number of directors as independent directors. The Central Government may prescribe the minimum number of independent directors in case of any class or classes of companies.", "relatedSection": 149, "category": "Directors"},
        {"number": "8.2", "title": "Companies (Appointment and Qualification of Directors) Rules, 2014 — Woman Director", "text": "The following class of companies shall appoint at least one woman director— (i) every listed company; (ii) every other public company having paid-up share capital of one hundred crore rupees or more; or turnover of three hundred crore rupees or more.", "relatedSection": 149, "category": "Directors"},
        {"number": "9.1", "title": "Companies (Meetings of Board and its Powers) Rules, 2014 — Board Meetings", "text": "One meeting of the Board of Directors in each half of a calendar year with a gap of not less than ninety days between the two meetings and the participation of directors through video conferencing or other audio visual means shall be counted for the purposes of quorum under section 174.", "relatedSection": 173, "category": "Board Meetings"},
        {"number": "9.2", "title": "Companies (Meetings of Board and its Powers) Rules, 2014 — Audit Committee", "text": "Following class of companies shall constitute an Audit Committee— (i) all listed companies; (ii) all public companies with a paid-up capital of ten crore rupees or more; (iii) all public companies having turnover of one hundred crore rupees or more; (iv) all public companies having aggregate outstanding loans, debentures and deposits exceeding fifty crore rupees.", "relatedSection": 177, "category": "Board Committees"},
        {"number": "10.1", "title": "Companies (Appointment and Remuneration of Managerial Personnel) Rules, 2014", "text": "Every listed company and every public company having a paid-up share capital of ten crore rupees or more shall have whole-time key managerial personnel.", "relatedSection": 203, "category": "Managerial Personnel"},
        {"number": "11.1", "title": "Companies (Audit and Auditors) Rules, 2014 — Appointment", "text": "The auditor shall be appointed for a term of five consecutive years from the conclusion of the annual general meeting at which such appointment is made till the conclusion of the fifth consecutive annual general meeting held after that meeting.", "relatedSection": 139, "category": "Audit"},
        {"number": "11.2", "title": "Companies (Audit and Auditors) Rules, 2014 — Rotation", "text": "The listed companies and the following class of companies excluding one person companies and small companies shall comply with the requirements of auditor rotation — (a) all unlisted public companies having paid up share capital of rupees ten crore or more; (b) all private limited companies having paid up share capital of rupees fifty crore or more.", "relatedSection": 139, "category": "Audit"},
        {"number": "12.1", "title": "Companies (Corporate Social Responsibility Policy) Rules, 2014", "text": "Every company having net worth of rupees five hundred crore or more, or turnover of rupees one thousand crore or more, or a net profit of rupees five crore or more during the immediately preceding financial year shall comply with the provisions of section 135 and these rules.", "relatedSection": 135, "category": "CSR"},
        {"number": "13.1", "title": "Companies (Prospectus and Allotment of Securities) Rules, 2014 — Private Placement", "text": "A company may make private placement to not more than fifty persons in each kind of security in a financial year, excluding qualified institutional buyers and employees of the company who are offered securities under a scheme of employees stock option.", "relatedSection": 42, "category": "Securities"},
        {"number": "14.1", "title": "Companies (Management and Administration) Rules, 2014 — Annual General Meeting", "text": "Every company shall hold its first annual general meeting within nine months from the date of closing of the first financial year of the company. In any other case, within six months from the date of closing of the financial year.", "relatedSection": 96, "category": "Management"},
    ],
}

# Cross-references between sections
cross_references = [
    {"fromSection": 3, "toSection": 2, "context": "Uses definitions of public company and private company from Section 2"},
    {"fromSection": 4, "toSection": 7, "context": "Memorandum required for incorporation under Section 7"},
    {"fromSection": 5, "toSection": 4, "context": "Articles supplement the memorandum under Section 4"},
    {"fromSection": 7, "toSection": 4, "context": "Incorporation requires filing of memorandum under Section 4"},
    {"fromSection": 7, "toSection": 5, "context": "Incorporation requires filing of articles under Section 5"},
    {"fromSection": 42, "toSection": 23, "context": "Private placement is one method of issuing securities under Section 23"},
    {"fromSection": 62, "toSection": 43, "context": "Further issue relates to kinds of share capital under Section 43"},
    {"fromSection": 68, "toSection": 52, "context": "Buy-back may use securities premium account under Section 52"},
    {"fromSection": 123, "toSection": 127, "context": "Failure to pay declared dividend invokes punishment under Section 127"},
    {"fromSection": 139, "toSection": 143, "context": "Appointed auditor shall exercise powers under Section 143"},
    {"fromSection": 139, "toSection": 147, "context": "Contravention of appointment provisions punishable under Section 147"},
    {"fromSection": 149, "toSection": 152, "context": "Directors appointed under procedure in Section 152"},
    {"fromSection": 149, "toSection": 166, "context": "Directors shall perform duties as specified in Section 166"},
    {"fromSection": 149, "toSection": 164, "context": "Directors must not be disqualified under Section 164"},
    {"fromSection": 177, "toSection": 149, "context": "Audit committee requires independent directors appointed under Section 149"},
    {"fromSection": 178, "toSection": 149, "context": "Nomination committee requires independent directors under Section 149"},
    {"fromSection": 185, "toSection": 186, "context": "Loans to directors related to general loan provisions under Section 186"},
    {"fromSection": 196, "toSection": 197, "context": "Remuneration of managing director subject to limits under Section 197"},
    {"fromSection": 196, "toSection": 203, "context": "Managing director is key managerial personnel under Section 203"},
    {"fromSection": 447, "toSection": 448, "context": "False statements constitute fraud under Section 447"},
    {"fromSection": 462, "toSection": 469, "context": "Rule-making power complements Schedule amendment power under Section 469"},
    {"fromSection": 270, "toSection": 271, "context": "Petition for winding up under Section 271 invokes grounds in Section 270"},
]
