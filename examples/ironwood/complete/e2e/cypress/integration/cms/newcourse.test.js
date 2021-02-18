
describe("Studio home page", () => {
    const lms_url = Cypress.env("LMS_URL");
    const cms_url = Cypress.env("CMS_URL");
  
    it("test if an Admin able to create new course", async () => {
      cy.visit(lms_url)
      cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
      cy.visit(cms_url)
      cy.createCourse();
      cy.visit(cms_url);
      cy.get("body").find("ul.list-courses").then(res => {
        if (res[0].children.length > 0) {
          cy.get(".course-item").should("be.visible") ;
          cy.get(".course-item:last-child").click() ;

        } else {
         alert("No Courses");
        }
      });
      
    });
  });