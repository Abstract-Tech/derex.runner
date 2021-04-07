describe("Courses Page", () => {
    const lms_url = Cypress.env("LMS_URL");
  
    it("test after you logged in you are able to navigate to courses page and check if there is courses or not  ", function() {
        cy.visit(lms_url);
        cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
        cy.url().should("include", "/login");
        cy.get("#login-email").type("staff@example.com");
        cy.get("#login-password").type("secret");
        cy.get(".action").click();
        cy.url().should("include", "/");
        cy.wait(2000)
      cy.visit("/courses");
  
      cy.get("body").find("ul.courses-listing.courses-list").then(res => {
        if (res[0].children.length > 0) {
          cy.get(".course").should("be.visible") ;
        } else {
          alert("No Courses");
        }
      });
    });
  });