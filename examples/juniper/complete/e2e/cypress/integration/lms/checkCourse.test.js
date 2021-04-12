describe("checkcourse test", () => {
  const lms_url = Cypress.env("LMS_URL");

  it("user can check the course", () => {

    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));


    cy.visit('/courses');
    // enter to the first course on the list

    cy.get(".course:nth-child(1)").click();
    cy.get("body").find("div.main-cta").then(res => {
      if (cy.get(res).children().length > 0) {
        cy.get(".register").then(($button) => {
          cy.wrap($button).click();
        });
      }
      else {
        cy.get("strong").then(($button) => {
          cy.wrap($button).click();
        });
      }
    })

    cy.get(".form-actions > .action-resume-course")
      .contains("Start Course")
      .then(($button) => {
        cy.wrap($button).click();
      });
    cy.visit(
      `${lms_url}/courses/course-v1:Abstract+101+2021/courseware/d8a6192ade314473a78242dfeedfbf5b/edx_introduction/`
    );

  });
});