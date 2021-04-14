// describe("Schedule & Details settings test", () => {
//     const lms_url = Cypress.env("LMS_URL");
//     const course_id = Cypress.env("DEMO_COURSE_ID");
//     const cms_url = Cypress.env("CMS_URL");
//     const demo_course = `${cms_url}/course/${course_id}`;

//     it("allows admin to change sittings ", () => {

//       cy.visit(lms_url)
//       cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
//       cy.visit(demo_course)

//       // go to  Schedule & Details settings

//       cy
//         .get(".nav-course-settings > .title")
//         .click({ force: true });

//       cy
//       cy.get('.nav-course-settings-schedule > a')

//         .click({ force: true });

//         cy.get('#course-short-description').clear().type("test the description text");
//         cy.get('.nav-actions > ul > :nth-child(1) > .action-primary').click();

//         cy.get('#course-start-time').clear().type("12:00");
//         cy.get('.nav-actions > ul > :nth-child(1) > .action-primary').click();

//     })

//   });
