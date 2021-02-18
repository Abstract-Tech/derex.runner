describe("Studio home page", () => {
    const cms_url = Cypress.env("CMS_URL");
  const course_id = Cypress.env("DEMO_COURSE_ID");
  const export_url = `${cms_url}/export/${course_id}`;
  
    it("test if an Admin able import course", async () => {
      cy.visit(lms_url)
      cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
      cy.visit(cms_url)
      cy.createCourse();
      cy.visit(cms_url);
      cy.get("body").find("ul.list-courses").then(res => {
        if (res[0].children.length > 0) {
          cy.get(".course-item").should("be.visible");
          cy.get(".course-item:last-child").click();
          cy.get('.nav-course-tools > .title').click()
          cy.get('.nav-course-tools-export > a').click();
          cy.get("a.action-export").click();
        } else {
         alert("No Courses");
        }
      });
      
    });
  });