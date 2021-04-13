describe("Studio home page", () => {
    const lms_url = Cypress.env("LMS_URL");
    const cms_url = Cypress.env("CMS_URL");
  
    it("test if an Admin able to create new course", async () => {
      cy.visit(lms_url)
      cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
      cy.visit(cms_url)
      cy.get(".nav-actions .new-course-button").wait(500).click();
      // fill the form up
      cy.get("#new-course-name").type("course");
      cy.get("#new-course-org").type("Abstract");
      cy.get("#new-course-number").type("Lm101");
      cy.get("#new-course-run").type("2021");
      // click to submite the form
      cy.get(".new-course-save").wait(10).click();
    });
  });