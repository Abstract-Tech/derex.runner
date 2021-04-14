// describe("create section + subsection + unit in exsist course", () => {
//     const lms_url = Cypress.env("LMS_URL");
//     const course_id = Cypress.env("DEMO_COURSE_ID");
//     const cms_url = Cypress.env("CMS_URL");
//     const demo_course = `${cms_url}/course/${course_id}`;

//     it("allows admin to change sittings ", () => {

//       cy.visit(lms_url)
//       cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
//       cy.visit(demo_course)
//       cy.get('ul > :nth-child(1) > .button').click({ force: true });

//     });
//   });
