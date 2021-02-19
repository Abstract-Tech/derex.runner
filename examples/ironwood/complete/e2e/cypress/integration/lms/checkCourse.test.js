describe("checkcourse test", () => {
    const lms_url = Cypress.env("LMS_URL");
    const mailslurper_url = Cypress.env("MAILSLURPER_URL");
  
    it("user can check the course", () => {
      cy.login(lms_url, Cypress.env("user_email"), Cypress.env("user_password"));
      cy.url().should("include", "/dashboard");
  
      cy.visit(`${lms_url}/courses`);
      // enter to the first course on the list
  
      cy.get(".course:nth-child(1)").click();
  
      cy.get(".register").then(($button) => {
        cy.wrap($button).click();
      });
      cy.get("strong").then(($button) => {
        cy.wrap($button).click();
      });
  
      cy.get(".form-actions > .action-resume-course")
        .contains("Start Course")
        .then(($button) => {
          cy.wrap($button).click();
        });
      cy.visit(
        `${lms_url}/courses/course-v1:Abstract+EX989+2019_9/courseware/e317b7ccdb5f4020bf01dd2e1107df88/ae6cd2ceb3fd40c18d740e73c16b33d3/?child=first`
      );
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 1"] .field:nth-child(3) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 2"] .field:nth-child(2) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 3"] .field:nth-child(4) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 4"] .field:nth-child(4) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 5"] .field:nth-child(4) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 6"] .field:nth-child(4) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 7"] .field:nth-child(4) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 8"] .field:nth-child(4) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 9"] .field:nth-child(4) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
      cy.get(
        '.problem .wrapper-problem-response[aria-label="Question 10"] .field:nth-child(4) label'
      ).then(($button) => {
        cy.wrap($button).click();
      });
  
      cy.get(".submit-attempt-container button")
        .should("be.visible")
        .then(($button) => {
          cy.wrap($button).click();
        });
      cy.get(".notification-message").should("be.visible");
    });
  });