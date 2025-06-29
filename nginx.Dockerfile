# -------- Stage 1: Flutter build --------
FROM dart:stable AS flutter-builder

# Install Flutter
RUN git clone https://github.com/flutter/flutter.git -b stable --depth 1 /flutter
ENV PATH="/flutter/bin:/flutter/bin/cache/dart-sdk/bin:$PATH"
RUN flutter doctor -v

# Clone your frontend project (adjust this!)
RUN git clone https://github.com/vnonnenmacher/sepsis_agent_app.git /app
WORKDIR /app

# Enable web + build
RUN flutter config --enable-web
RUN flutter pub get
RUN flutter build web

# -------- Stage 2: Serve via NGINX --------
FROM nginx:alpine

# Include MIME types so CSS/JS work correctly
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Copy built frontend from builder stage
COPY --from=flutter-builder /app/build/web /usr/share/nginx/html
