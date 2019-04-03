package com._360ec.ctf;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;


public class SuperPass extends HttpServlet {
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String secret = getServletContext().getInitParameter("secret");
        String token =request.getParameter("token");
        String msg = "Token错误!";
        if (token == null) {
            this.doGet(request, response);
            return;
        }

        if (secret.compareTo(token.trim()) == 0) {
            msg = "Token输入正确!";
        }
        request.setAttribute("msg", msg);
        this.doGet(request, response);
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        RequestDispatcher view = request.getRequestDispatcher("WEB-INF/templates/login.jsp");
        view.forward(request, response);
    }
}
