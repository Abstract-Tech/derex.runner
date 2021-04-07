describe("Knowledge Base Application", () => {
  const lms_url = Cypress.env("LMS_URL");

  // previous test omitted for brevity
  it("Should be able to login: admin", function () {
    cy.visit(lms_url);
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.url().should("include", "/login");
    cy.get("#login-email").type("staff@example.com");
    cy.get("#login-password").type("secret");
    cy.get(".action").click();
    cy.url().should("include", "/");
    cy.wait(2000)
    cy.visit("/dashboard");
  
    cy.get("body").find(".my-courses").then(res => {
      // if (res[0].children.length > 0) {
      //   cy.get(".course").should("be.visible") ;
      // } else {
      //  alert("No Courses");
      // }
  
});
});
})
